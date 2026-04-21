from defi_agent.models import PoolData
from defi_agent.brain.filters import passes_safety_belts

def test_safety_belts():
    # Good pool
    safe_pool = PoolData(pool="1", project="aave", chain="Ethereum", tvl_usd=60_000_000, apy=10, underlying_tokens=["USDC"], age_days=100, tvl_drop_24h_percent=5)
    assert passes_safety_belts(safe_pool) is True
    
    # TVL too low
    low_tvl = PoolData(pool="2", project="aave", chain="Ethereum", tvl_usd=40_000_000, apy=10, underlying_tokens=["USDC"], age_days=100, tvl_drop_24h_percent=5)
    assert passes_safety_belts(low_tvl) is False
    
    # Not a stablecoin/bluechip
    bad_token = PoolData(pool="3", project="aave", chain="Ethereum", tvl_usd=60_000_000, apy=10, underlying_tokens=["SHIB"], age_days=100, tvl_drop_24h_percent=5)
    assert passes_safety_belts(bad_token) is False
    
    # Too young
    young = PoolData(pool="4", project="aave", chain="Ethereum", tvl_usd=60_000_000, apy=10, underlying_tokens=["USDC"], age_days=30, tvl_drop_24h_percent=5)
    assert passes_safety_belts(young) is False
    
    # Bank run (TVL drop > 20%)
    bank_run = PoolData(pool="5", project="aave", chain="Ethereum", tvl_usd=60_000_000, apy=10, underlying_tokens=["USDC"], age_days=100, tvl_drop_24h_percent=25)
    assert passes_safety_belts(bank_run) is False