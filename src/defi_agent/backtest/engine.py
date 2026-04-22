from typing import List, Dict, Any
from defi_agent.models import PoolData, Position
from defi_agent.backtest.friction import FrictionModel
from defi_agent.brain.math_models import calculate_expected_value, calculate_kelly_size, calculate_divergence_score

class BacktestEngine:
    def __init__(self, initial_capital: float = 10000.0, cooldown_hours: int = 24):
        self.initial_capital = initial_capital
        self.idle_cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.portfolio_history = []
        self.trade_logs = []
        self.cooldown_hours = cooldown_hours
        self.last_trade_times = {}
        self.blacklist = {} # pool_id -> expiry_timestamp
        self.friction_model = FrictionModel()

    def get_total_equity(self) -> float:
        return self.idle_cash + sum(p.amount for p in self.positions.values())

    def update_accrual(self, multi_pool_data_snapshot: Dict[str, PoolData], hours: float):
        for p_id, pos in list(self.positions.items()):
            pool_data = multi_pool_data_snapshot.get(p_id)
            if pool_data:
                interest = pos.amount * (pool_data.apy / 100.0) * (hours / (365.0 * 24.0))
                pos.amount += interest

    def execute_trade(self, timestamp: int, pool: PoolData, action: str, amount: float) -> bool:
        # Check Cooldown
        if pool.pool in self.last_trade_times:
            if (timestamp - self.last_trade_times[pool.pool]) / 3600 < self.cooldown_hours:
                return False
        
        # Check Blacklist
        if pool.pool in self.blacklist:
            if timestamp < self.blacklist[pool.pool]:
                return False

        gas = self.friction_model.estimate_gas_cost(15.0)
        slippage = self.friction_model.calculate_slippage(amount, pool.tvl_usd)
        
        if action == "DEPOSIT":
            cost = gas + slippage
            if self.idle_cash < (amount + cost): return False
            self.idle_cash -= (amount + cost)
            if pool.pool in self.positions: self.positions[pool.pool].amount += amount
            else: self.positions[pool.pool] = Position(pool.pool, amount, timestamp, pool.apy)
        elif action == "WITHDRAW":
            if pool.pool not in self.positions: return False
            withdraw_amt = min(amount, self.positions[pool.pool].amount)
            self.positions[pool.pool].amount -= withdraw_amt
            self.idle_cash += (withdraw_amt - gas)
            if self.positions[pool.pool].amount < 1.0: del self.positions[pool.pool]
        
        self.last_trade_times[pool.pool] = timestamp
        self.trade_logs.append({
            "ts": timestamp, "pool": pool.pool, "act": action, 
            "amt": amount, "total": self.get_total_equity()
        })
        return True

    def run_simulation(self, multi_pool_data: Dict[str, List[Dict]], baseline_apy: float = 5.0):
        all_ts = sorted(list(set([d["timestamp"] for pools in multi_pool_data.values() for d in pools])))
        baseline_capital = self.initial_capital
        
        for i, ts in enumerate(all_ts):
            current_map = {}
            for p_id, hourly_list in multi_pool_data.items():
                data = next((d for d in hourly_list if d["timestamp"] == ts), None)
                if data:
                    current_map[p_id] = PoolData(
                        pool=p_id, project=data.get("project", "N/A"), chain="ETH",
                        tvl_usd=data.get("tvl_usd", 100_000_000), apy=data["apy"], underlying_tokens=["USDC"],
                        tvl_drop_24h_percent=data.get("tvl_drop_24h", 0.0), 
                        apy_spike_24h_percent=data.get("apy_spike_24h", 0.0),
                        age_days=100
                    )
            
            if i > 0:
                self.update_accrual(current_map, 1.0)
                baseline_capital += baseline_capital * (baseline_apy / 100.0) * (1.0 / (365.0 * 24.0))

            total_equity = self.get_total_equity()
            for p_id, pool in current_map.items():
                
                # --- MONITORING: SMELL TEST (DIVERGENCE) ---
                div_score = calculate_divergence_score(pool)
                if p_id in self.positions:
                    if div_score > 50:
                        self.execute_trade(ts, pool, "WITHDRAW", self.positions[p_id].amount)
                        self.trade_logs[-1]["reason"] = "Smell Test L3: Extreme Divergence"
                        self.blacklist[p_id] = ts + (48 * 3600) # Blacklist 48h
                    elif div_score > 30:
                        self.execute_trade(ts, pool, "WITHDRAW", self.positions[p_id].amount * 0.5)
                        self.trade_logs[-1]["reason"] = "Smell Test L2: High Divergence"
                
                # --- MONITORING: STANDARD RISK ---
                if p_id in self.positions:
                    if pool.tvl_drop_24h_percent > 20 or pool.apy < (baseline_apy * 0.5):
                        self.execute_trade(ts, pool, "WITHDRAW", self.positions[p_id].amount)
                        self.trade_logs[-1]["reason"] = "Kill Switch: Safety/Yield Collapse"
                        self.blacklist[p_id] = ts + (24 * 3600)

                # --- DECISION: NEW DEPOSITS ---
                if p_id not in self.positions:
                    # Don't evaluate if blacklisted
                    if p_id in self.blacklist and ts < self.blacklist[p_id]:
                        continue

                    friction_est = 30.0
                    ev = calculate_expected_value(pool, total_equity * 0.1, 7, friction_est)
                    if ev > 0:
                        target_pct = calculate_kelly_size(ev, total_equity * 0.1)
                        target_amt = total_equity * target_pct
                        if target_amt > 500:
                            self.execute_trade(ts, pool, "DEPOSIT", target_amt)
            
            self.portfolio_history.append({"timestamp": ts, "capital": total_equity, "baseline": baseline_capital})
