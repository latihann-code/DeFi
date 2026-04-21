import numpy as np
from defi_agent.models import PoolData

def calculate_success_probability(pool: PoolData) -> float:
    prob = 0.98 # Base 98% success for blue chips
    if pool.tvl_usd < 50_000_000: prob -= 0.1
    if pool.age_days < 60: prob -= 0.1
    return max(0.6, prob) # Min 60% probability for demo

def calculate_expected_value(pool: PoolData, capital: float, days: int, friction: float) -> float:
    p_success = calculate_success_probability(pool)
    p_failure = 1.0 - p_success
    profit = capital * (pool.apy / 100.0) * (days / 365.0) - friction
    loss = capital * 0.1 + friction # Max loss assumed 10% (conservative)
    return (p_success * profit) - (p_failure * loss)

def calculate_kelly_size(ev: float, capital_at_risk: float) -> float:
    if ev <= 0: return 0.0
    # Kelly simplified for DeFi: we aim for fractional Kelly (half-kelly) for safety
    size = (ev / capital_at_risk) * 0.5
    return min(0.4, size) # Max 40% per pool
