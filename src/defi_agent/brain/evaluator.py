# src/defi_agent/brain/evaluator.py
from typing import List, Dict, Any
from defi_agent.models import PoolData
from defi_agent.brain.filters import passes_safety_belts
from defi_agent.brain.math_models import calculate_trade_edge

def evaluate_opportunities(
    pools: List[PoolData],
    capital: float,
    days: int,
    token_approval_gas: float,
    swap_slippage_percent: float,
    deposit_gas: float,
    withdraw_gas: float,
    hidden_costs: float
) -> List[Dict[str, Any]]:
    
    signals = []
    
    for pool in pools:
        if not passes_safety_belts(pool):
            continue
            
        swap_slippage = capital * (swap_slippage_percent / 100.0)
        
        edge = calculate_trade_edge(
            pool=pool,
            capital=capital,
            days=days,
            token_approval_gas=token_approval_gas,
            swap_slippage=swap_slippage,
            deposit_gas=deposit_gas,
            withdraw_gas=withdraw_gas,
            hidden_costs=hidden_costs
        )
        
        if edge > 0:
            signals.append({
                "action": "DEPOSIT",
                "pool": pool.pool,
                "project": pool.project,
                "asset": pool.underlying_tokens[0] if pool.underlying_tokens else "UNKNOWN",
                "amount": capital,
                "expected_adjusted_apy": pool.apy - pool.apy_volatility_penalty - pool.inflation_discount,
                "trade_edge": edge
            })
            
    return signals
