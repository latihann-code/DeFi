from typing import List, Dict, Any
from defi_agent.models import PoolData
from defi_agent.brain.evaluator import evaluate_opportunities
from defi_agent.backtest.friction import FrictionModel

class BacktestEngine:
    def __init__(self, initial_capital: float = 10000.0, cooldown_hours: int = 24):
        self.capital = initial_capital
        self.portfolio_history = []
        self.trade_logs = []
        self.cooldown_hours = cooldown_hours
        self.last_trade_times = {} # pool_id -> timestamp
        self.friction_model = FrictionModel()

    def execute_trade(self, timestamp: int, pool: PoolData, action: str, amount: float) -> bool:
        """
        Mengeksekusi trade dengan pengecekan cooldown.
        """
        # Cek Cooldown
        if pool.pool in self.last_trade_times:
            elapsed_hours = (timestamp - self.last_trade_times[pool.pool]) / 3600
            if elapsed_hours < self.cooldown_hours:
                return False
        
        # Simulasi Friction (Gas & Slippage)
        gas_cost = self.friction_model.estimate_gas_cost(base_gas_usd=15.0)
        slippage = self.friction_model.calculate_slippage(capital=amount, pool_tvl=pool.tvl_usd)
        
        total_cost = gas_cost + slippage
        
        # Update capital & logs
        self.capital -= total_cost
        self.last_trade_times[pool.pool] = timestamp
        self.trade_logs.append({
            "timestamp": timestamp,
            "pool": pool.pool,
            "action": action,
            "amount": amount,
            "cost": total_cost
        })
        
        return True

    def run_stage_1(self, hourly_data: List[Dict], pool_id: str, project: str):
        """
        Stage 1: Historical Replay (Normal Condition)
        """
        for data in hourly_data:
            ts = data["timestamp"]
            apy = data["apy"]
            tvl = data.get("tvl_usd", 100_000_000)
            
            # Buat object PoolData mock untuk evaluator
            pool = PoolData(
                pool=pool_id, 
                project=project, 
                chain="Ethereum", 
                tvl_usd=tvl, 
                apy=apy, 
                underlying_tokens=["USDC"], 
                age_days=100
            )
            
            # Panggil AI Brain Evaluator
            # Gunakan Minimum Edge Margin: Expected Profit > Friction * 1.5 (implicit in math_models or handled here)
            signals = evaluate_opportunities(
                pools=[pool],
                capital=self.capital,
                days=7, # Time horizon
                token_approval_gas=1.5,
                swap_slippage_percent=0.5,
                deposit_gas=3.0,
                withdraw_gas=3.0,
                hidden_costs=2.0
            )
            
            if signals:
                # Ambil signal pertama dan eksekusi jika margin cukup (sudah difilter di evaluator.py)
                self.execute_trade(timestamp=ts, pool=pool, action=signals[0]["action"], amount=signals[0]["amount"])
            
            # Log portfolio value harian (opsional, untuk metrics)
            self.portfolio_history.append({"timestamp": ts, "capital": self.capital})
