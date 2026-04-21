# src/defi_agent/brain/math_models.py
from defi_agent.models import PoolData

def calculate_trade_edge(
    pool: PoolData,
    capital: float,
    days: int,
    token_approval_gas: float,
    swap_slippage: float,
    deposit_gas: float,
    withdraw_gas: float,
    hidden_costs: float
) -> float:
    
    adjusted_apy = pool.apy - pool.apy_volatility_penalty - pool.inflation_discount
    
    net_expected_profit = capital * (adjusted_apy / 100.0) * (days / 365.0)
    
    friction = token_approval_gas + swap_slippage + deposit_gas + withdraw_gas + hidden_costs
    
    trade_edge = net_expected_profit - friction
    return trade_edge
