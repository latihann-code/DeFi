from defi_agent.models import PoolData
from defi_agent.brain.filters import passes_safety_belts

def test_safety_belts():
    # Good pool
    safe_pool = PoolData(pool="1", project="aave", chain="Ethereum", tvl_usd=100_000_000_000, apy=10, underlying_tokens=["USDC"], age_days=365, tvl_drop_24h_percent=0)
    assert passes_safety_belts(safe_pool) is True
    
    # TVL too low (predator needs 100k)
    low_tvl = PoolData(pool="2", project="aave", chain="Ethereum", tvl_usd=50_000, apy=10, underlying_tokens=["USDC"], age_days=365, tvl_drop_24h_percent=0)
    assert passes_safety_belts(low_tvl) is False
    
    # Bank run (TVL drop > 20% drops risk score too low)
    bank_run = PoolData(pool="5", project="aave", chain="Ethereum", tvl_usd=100_000, apy=10, underlying_tokens=["USDC"], age_days=0, tvl_drop_24h_percent=25)
    assert passes_safety_belts(bank_run) is False