# src/defi_agent/brain/math_models.py
from defi_agent.models import PoolData

def calculate_risk_score(pool: PoolData) -> float:
    """
    Menghitung skor risiko (0.0 - 1.0). 1.0 = Sangat Aman.
    Faktor: TVL, Age, dan TVL Stability.
    """
    score = 1.0
    # Penalti TVL Kecil
    if pool.tvl_usd < 100_000_000: score *= 0.8
    if pool.tvl_usd < 10_000_000: score *= 0.5
    
    # Penalti Umur (Lindy Effect)
    if pool.age_days < 30: score *= 0.5
    if pool.age_days < 90: score *= 0.8
    
    # Penalti Volatilitas TVL
    if pool.tvl_drop_24h_percent > 10: score *= 0.7
    
    return score

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
    # 1. Hitung Risk Score
    risk_score = calculate_risk_score(pool)
    
    # 2. Adjusted APY (Bunga yang sudah didiskon risiko)
    # Kita juga kurangi volatility penalty & inflation
    base_adj_apy = (pool.apy - pool.apy_volatility_penalty - pool.inflation_discount) * risk_score
    
    # 3. Amortized Friction
    # Berapa biaya 'harian' untuk masuk ke pool ini?
    total_friction = token_approval_gas + swap_slippage + deposit_gas + withdraw_gas + hidden_costs
    
    # 4. Net Profit over duration
    expected_profit = capital * (base_adj_apy / 100.0) * (days / 365.0)
    
    # Trade Edge = Profit - Friction
    return expected_profit - total_friction
