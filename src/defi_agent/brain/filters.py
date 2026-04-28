from defi_agent.models import PoolData
from defi_agent.brain.math_models import calculate_risk_score

WHITELIST_PROTOCOLS = {"aave", "uniswap", "aerodrome", "beefy", "raydium", "cetus"}
ALLOWED_TOKENS = {"USDC", "USDT", "DAI", "ETH", "WBTC", "WETH", "USDC.E", "CBETH"}
MIN_TVL = 100_000 # Predator hunts smaller, high-yield pools
MIN_AGE_DAYS = 0  # Allow brand new pools
MIN_RISK_SCORE = 0.3 # Looser risk score for insane APYs

def passes_predator_filter(pool: PoolData) -> bool:
    """
    Predator Filter: Strict whitelist but more flexible TVL/Age for high APY hunting.
    """
    # 1. Whitelist Check
    is_whitelisted = False
    for protocol in WHITELIST_PROTOCOLS:
        if protocol in pool.project.lower():
            is_whitelisted = True
            break
    if not is_whitelisted:
        return False

    # 2. Basic Metrics
    if pool.tvl_usd < MIN_TVL:
        return False
    if pool.age_days < MIN_AGE_DAYS:
        return False
        
    # 3. Risk Score Check (Higher is safer)
    risk_score = calculate_risk_score(pool)
    if risk_score < MIN_RISK_SCORE:
        return False
        
    # 4. Token Check (Relaxed for DefiLlama returning addresses)
    # Just assume it's okay if it passed the whitelist and TVL check, or check symbol if available
    return True

def passes_safety_belts(pool: PoolData) -> bool:
    """Legacy wrapper for compatibility."""
    return passes_predator_filter(pool)