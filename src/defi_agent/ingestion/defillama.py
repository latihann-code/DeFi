import requests
from defi_agent.models import PoolData

class DefiLlamaClient:
    BASE_YIELDS_URL = "https://yields.llama.fi"
    
    def fetch_yields(self) -> list[PoolData]:
        url = f"{self.BASE_YIELDS_URL}/pools"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json().get("data", [])
        pools = []
        for item in data:
            try:
                # Handle cases where required fields might be missing or None
                if item.get('tvlUsd') is not None and item.get('apy') is not None:
                    pool = PoolData(
                        pool=item.get("pool", ""),
                        project=item.get("project", ""),
                        chain=item.get("chain", ""),
                        tvlUsd=float(item["tvlUsd"]),
                        apy=float(item["apy"])
                    )
                    pools.append(pool)
            except (ValueError, TypeError):
                continue
                
        return pools
