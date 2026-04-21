from defi_agent.models import PoolData
import responses
import requests
from defi_agent.ingestion.defillama import DefiLlamaClient

def test_pool_data_model():
    data = {
        "pool": "0x123",
        "project": "aave",
        "chain": "Ethereum",
        "tvlUsd": 1000000,
        "apy": 5.5
    }
    pool = PoolData(
        pool=data["pool"],
        project=data["project"],
        chain=data["chain"],
        tvl_usd=data["tvlUsd"],
        apy=data["apy"]
    )
    assert pool.pool == "0x123"
    assert pool.project == "aave"
    assert pool.chain == "Ethereum"
    assert pool.tvl_usd == 1000000
    assert pool.apy == 5.5

@responses.activate
def test_fetch_yields():
    mock_response = {
        "status": "success",
        "data": [
            {
                "pool": "0xabc",
                "project": "lido",
                "chain": "Ethereum",
                "tvlUsd": 5000000,
                "apy": 4.2
            }
        ]
    }
    responses.add(
        responses.GET,
        "https://yields.llama.fi/pools",
        json=mock_response,
        status=200
    )
    
    client = DefiLlamaClient()
    pools = client.fetch_yields()
    
    assert len(pools) == 1
    assert pools[0].project == "lido"
    assert pools[0].tvl_usd == 5000000

@responses.activate
def test_fetch_yields_api_error():
    responses.add(
        responses.GET,
        "https://yields.llama.fi/pools",
        status=500
    )
    
    client = DefiLlamaClient()
    pools = client.fetch_yields()
    
    # We want it to handle the error gracefully and return an empty list for now
    # or we might want to raise a custom exception. Let's return empty list for resilience.
    assert pools == []

def test_expanded_pool_data():
    from defi_agent.models import PoolData
    data = {
        "pool": "0xabc",
        "project": "aave-v3",
        "chain": "Ethereum",
        "tvl_usd": 100000000.0,
        "apy": 8.5,
        "underlying_tokens": ["USDC"],
        "age_days": 120,
        "tvl_drop_24h_percent": 5.0,
        "apy_volatility_penalty": 1.5,
        "inflation_discount": 0.5
    }
    pool = PoolData(**data)
    assert pool.underlying_tokens == ["USDC"]
    assert pool.age_days == 120
    assert pool.tvl_drop_24h_percent == 5.0
    assert pool.apy_volatility_penalty == 1.5
    assert pool.inflation_discount == 0.5
