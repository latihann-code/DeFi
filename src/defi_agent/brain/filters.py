from defi_agent.models import PoolData

ALLOWED_TOKENS = {"USDC", "USDT", "DAI", "ETH", "WBTC"}
MIN_TVL = 50_000_000
MIN_AGE_DAYS = 90
MAX_TVL_DROP_PERCENT = 20.0

def passes_safety_belts(pool: PoolData) -> bool:
    if pool.tvl_usd < MIN_TVL:
        return False
        
    if pool.age_days < MIN_AGE_DAYS:
        return False
        
    if pool.tvl_drop_24h_percent > MAX_TVL_DROP_PERCENT:
        return False
        
    # Check if ANY underlying token is NOT in the allowed list
    if not pool.underlying_tokens:
        return False # Reject empty
        
    for token in pool.underlying_tokens:
        if token not in ALLOWED_TOKENS:
            return False
            
    return True