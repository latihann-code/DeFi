from defi_agent.models import PoolData

def test_pool_data_model():
    data = {
        "pool": "0x123",
        "project": "aave",
        "chain": "Ethereum",
        "tvlUsd": 1000000,
        "apy": 5.5
    }
    pool = PoolData(**data)
    assert pool.pool == "0x123"
    assert pool.project == "aave"
    assert pool.chain == "Ethereum"
    assert pool.tvl_usd == 1000000
    assert pool.apy == 5.5
