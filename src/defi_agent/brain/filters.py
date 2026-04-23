from defi_agent.models import PoolData
from defi_agent.brain.math_models import calculate_risk_score

WHITELIST_PROTOCOLS = {"aave", "uniswap", "aerodrome", "beefy"}
ALLOWED_TOKENS = {"USDC", "USDT", "DAI", "ETH", "WBTC", "WETH", "USDC.e", "CBETH"}
MIN_TVL = 1_000_000
MIN_AGE_DAYS = 30
MIN_RISK_SCORE = 0.7

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
        
    # 4. Token Check (Optional, but safe)
    if not pool.underlying_tokens:
        return False
    
    # Check if ANY underlying token is in the allowed list (at least one)
    has_allowed_token = False
    for token in pool.underlying_tokens:
        if token.upper() in ALLOWED_TOKENS:
            has_allowed_token = True
            break
            
    return has_allowed_token

def passes_safety_belts(pool: PoolData) -> bool:
    """Legacy wrapper for compatibility."""
    return passes_predator_filter(pool)