from typing import List, Dict, Any
from defi_agent.models import PoolData
from defi_agent.brain.evaluator import evaluate_opportunities
from defi_agent.backtest.friction import FrictionModel

class BacktestEngine:
    def __init__(self, initial_capital: float = 10000.0, cooldown_hours: int = 24):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.portfolio_history = [] # List[Dict] (ts, capital, baseline)
        self.trade_logs = []
        self.cooldown_hours = cooldown_hours
        self.last_trade_times = {} # pool_id -> timestamp
        self.friction_model = FrictionModel()
        
        # Position Tracking
        self.current_pool_id = None
        self.current_pool_data = None # PoolData
        self.active_investment = 0.0 # Amount currently in a pool
        self.idle_cash = initial_capital # Amount not yet deployed

    def update_accrual(self, hours: float):
        """
        Menghitung akumulasi bunga (yield) berdasarkan APY pool saat ini.
        Laba ditambahkan ke active_investment.
        """
        if self.active_investment > 0 and self.current_pool_data:
            apy = self.current_pool_data.apy
            # Formula: interest = principal * (apy / 100) * (hours / 365 * 24)
            interest = self.active_investment * (apy / 100.0) * (hours / (365.0 * 24.0))
            self.active_investment += interest

    def execute_trade(self, timestamp: int, pool: PoolData, action: str, amount: float) -> bool:
        # Check Cooldown
        if pool.pool in self.last_trade_times:
            elapsed_hours = (timestamp - self.last_trade_times[pool.pool]) / 3600
            if elapsed_hours < self.cooldown_hours:
                return False
        
        # Simulasi Friction
        gas_cost = self.friction_model.estimate_gas_cost(base_gas_usd=15.0)
        slippage = self.friction_model.calculate_slippage(capital=amount, pool_tvl=pool.tvl_usd)
        total_friction = gas_cost + slippage
        
        if action == "DEPOSIT":
            if self.idle_cash < (amount + total_friction):
                return False
            self.idle_cash -= (amount + total_friction)
            self.active_investment += amount
            self.current_pool_id = pool.pool
            self.current_pool_data = pool
        elif action == "WITHDRAW":
            if self.active_investment < amount:
                return False
            # Penalti withdraw (gas)
            self.active_investment -= (amount + gas_cost)
            self.idle_cash += amount
            if self.active_investment <= 0:
                self.current_pool_id = None
                self.current_pool_data = None
        
        self.last_trade_times[pool.pool] = timestamp
        self.trade_logs.append({
            "timestamp": timestamp, "pool": pool.pool, "action": action, 
            "amount": amount, "cost": total_friction, "total_equity": self.get_total_equity()
        })
        return True

    def get_total_equity(self) -> float:
        return self.idle_cash + self.active_investment

    def run_simulation(self, multi_pool_data: Dict[str, List[Dict]], baseline_apy: float = 5.0):
        """
        Full Multi-Pool Simulation Loop.
        :param multi_pool_data: Dictionary {pool_id: list_of_hourly_data}
        """
        # Dapatkan daftar semua timestamp unik dari semua pool
        all_ts = set()
        for hourly_list in multi_pool_data.values():
            for d in hourly_list:
                all_ts.add(d["timestamp"])
        all_timestamps = sorted(list(all_ts))
        
        baseline_capital = self.initial_capital
        
        for i, ts in enumerate(all_timestamps):
            # 1. Update Accrual & Baseline
            if i > 0:
                self.update_accrual(hours=1.0)
                baseline_capital += baseline_capital * (baseline_apy / 100.0) * (1.0 / (365.0 * 24.0))
            
            # 2. Collect Current Data for all pools
            current_pools = []
            for p_id, hourly_list in multi_pool_data.items():
                data = next((d for d in hourly_list if d["timestamp"] == ts), None)
                if data:
                    pool_obj = PoolData(
                        pool=p_id, project=data.get("project", "Unknown"), chain="Ethereum",
                        tvl_usd=data.get("tvl_usd", 100_000_000), apy=data["apy"],
                        underlying_tokens=["USDC"], age_days=100,
                        tvl_drop_24h_percent=data.get("tvl_drop_24h", 0.0)
                    )
                    current_pools.append(pool_obj)
            
            # 3. Evaluate Opportunities (Brain)
            signals = evaluate_opportunities(
                pools=current_pools, capital=self.get_total_equity(), days=7,
                token_approval_gas=1.5, swap_slippage_percent=0.1,
                deposit_gas=5.0, withdraw_gas=5.0, hidden_costs=2.0
            )
            
            # 4. DECISION LOGIC: Reallocation / Switching
            if signals:
                best_signal = signals[0]
                
                if not self.current_pool_id:
                    self.execute_trade(timestamp=ts, pool=next(p for p in current_pools if p.pool == best_signal["pool"]), 
                                       action="DEPOSIT", amount=self.idle_cash * 0.95)
                
                elif self.current_pool_id != best_signal["pool"]:
                    current_pool_obj = next((p for p in current_pools if p.pool == self.current_pool_id), None)
                    if current_pool_obj:
                        # --- DISIPLIN PRO: Hysteresis Margin ---
                        # Hanya pindah jika APY pool baru > (APY pool sekarang + 15%)
                        if best_signal["expected_adjusted_apy"] > (current_pool_obj.apy + 15.0):
                            success_out = self.execute_trade(timestamp=ts, pool=current_pool_obj, action="WITHDRAW", amount=self.active_investment)
                            if success_out:
                                new_pool_obj = next(p for p in current_pools if p.pool == best_signal["pool"])
                                self.execute_trade(timestamp=ts, pool=new_pool_obj, action="DEPOSIT", amount=self.idle_cash * 0.95)
                                self.trade_logs[-1]["reason"] = "Hysteresis-Safe Switch: Net APY Gain > 15%"

            # 5. Log Equity Curve
            self.portfolio_history.append({
                "timestamp": ts, "capital": self.get_total_equity(), "baseline": baseline_capital
            })
