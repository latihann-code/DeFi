from defi_agent.models import PoolData
import responses
from defi_agent.ingestion.defillama import DefiLlamaClient

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
