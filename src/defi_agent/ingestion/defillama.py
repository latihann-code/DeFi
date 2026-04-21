import requests
from defi_agent.models import PoolData

class DefiLlamaClient:
    BASE_YIELDS_URL = "https://yields.llama.fi"
    
    def fetch_yields(self) -> list[PoolData]:
        url = f"{self.BASE_YIELDS_URL}/pools"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json().get("data", [])
        except (requests.RequestException, ValueError):
            return []
            
        pools = []
        for item in data:
            try:
                # Handle cases where required fields might be missing or None
                if item.get('tvlUsd') is not None and item.get('apy') is not None:
                    pool = PoolData(
                        pool=item.get("pool", ""),
                        project=item.get("project", ""),
                        chain=item.get("chain", ""),
                        tvl_usd=float(item["tvlUsd"]),
                        apy=float(item["apy"])
                    )
                    pools.append(pool)
            except (ValueError, TypeError):
                continue
                
        return pools
