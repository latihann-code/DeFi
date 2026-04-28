from defi_agent.models import PoolData
import math

def calculate_divergence_score(pool: PoolData) -> float:
    """
    Menghitung skor divergensi APY vs TVL.
    Divergence = (APY_Spike % - TVL_Change %)
    Output: 0.0 - 100.0
    """
    tvl_change = -pool.tvl_drop_24h_percent 
    divergence = pool.apy_spike_24h_percent - tvl_change
    return max(0.0, divergence)

def calculate_risk_score(pool: PoolData) -> float:
    """
    Sistem Reaksi Risiko (Non-Linear).
    Menggabungkan Weighted Score dengan Kill-Switch Behavior.
    """
    if pool.tvl_usd <= 0: tvl_s = 0
    else:
        tvl_s = min(0.9, (math.log10(pool.tvl_usd) - 6) / 3) # 10^6=$1M (0), 10^9=$1B (1)
        tvl_s = max(0.1, tvl_s)

    if pool.age_days < 30: age_s = 0.0
    elif pool.age_days < 90: age_s = 0.5
    else: age_s = min(1.0, pool.age_days / 365.0)

    max_drop = 20.0
    vol_s = max(0.0, 1.0 - (pool.tvl_drop_24h_percent / max_drop))
    audit_s = 1.0 if pool.audit_score >= 1.0 else 0.6 if pool.audit_score > 0 else 0.0

    weights = {"tvl": 0.30, "age": 0.20, "vol": 0.35, "audit": 0.15}
    base_score = (weights["tvl"] * tvl_s) + (weights["age"] * age_s) + (weights["vol"] * vol_s) + (weights["audit"] * audit_s)

    if vol_s < 0.3: base_score *= 0.5
    if vol_s == 0: return 0.0
    return base_score

def calculate_expected_value(pool: PoolData, capital: float, days: int, friction: float, momentum_score: float = 0.0) -> float:
    risk_score = calculate_risk_score(pool)
    if risk_score <= 0: return -999999
    
    p_success = risk_score
    p_failure = 1.0 - p_success
    
    adj_apy = pool.apy - pool.apy_volatility_penalty - pool.inflation_discount
    
    # OG Meta: Controlled Point Bonus (+10% relative boost to APY if points exist, capped)
    if pool.has_points:
        adj_apy *= 1.10
    
    # OG Meta: Momentum Boost
    if momentum_score > 0:
        adj_apy *= (1 + min(0.20, momentum_score / 100.0)) # Max 20% boost for hot chains
        
    profit = capital * (adj_apy / 100.0) * (days / 365.0) - friction
    loss = capital * 0.1 + friction
    return (p_success * profit) - (p_failure * loss)

def calculate_kelly_size(ev: float, capital_at_risk: float) -> float:
    if ev <= 0: return 0.0
    size = (ev / capital_at_risk) * 0.25
    return min(0.25, size)

def calculate_trade_edge(pool: PoolData, capital: float, days: int, token_approval_gas: float, swap_slippage: float, deposit_gas: float, withdraw_gas: float, hidden_costs: float) -> float:
    """Legacy wrapper for pure trade edge calculation (profit - friction)."""
    friction = token_approval_gas + swap_slippage + deposit_gas + withdraw_gas + hidden_costs
    adj_apy = pool.apy - pool.apy_volatility_penalty - pool.inflation_discount
    profit = capital * (adj_apy / 100.0) * (days / 365.0)
    return profit - friction
