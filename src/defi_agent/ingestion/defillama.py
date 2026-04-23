import requests
from defi_agent.models import PoolData

class DefiLlamaClient:
    BASE_YIELDS_URL = "https://yields.llama.fi"
    BASE_API_URL = "https://api.llama.fi"
    
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
                if item.get('tvlUsd') is not None and item.get('apy') is not None:
                    # Logic Predator: Detect Points protocols (Mocked for now)
                    points_protocols = ["aerodrome", "eigenlayer", "ethena", "pendle", "kamino"]
                    has_points = any(p in item.get("project", "").lower() for p in points_protocols)
                    
                    pool = PoolData(
                        pool=item.get("pool", ""),
                        project=item.get("project", ""),
                        chain=item.get("chain", ""),
                        tvl_usd=float(item["tvlUsd"]),
                        apy=float(item["apy"]),
                        underlying_tokens=item.get("underlyingTokens", []),
                        volume_usd=float(item.get("volumeUsd1d", 0)) if item.get("volumeUsd1d") else 0,
                        has_points=has_points
                    )
                    if not pool.underlying_tokens and item.get("symbol"):
                        pool.underlying_tokens = [item["symbol"]]
                    pools.append(pool)
            except (ValueError, TypeError):
                continue
        return pools

    def fetch_chain_momentum(self) -> dict:
        """
        Fetches chain TVL and 7d flow to identify hot chains.
        """
        url = f"{self.BASE_API_URL}/chains"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            # Sort by 7d TVL change
            momentum = sorted(data, key=lambda x: x.get("change_7d", 0) or 0, reverse=True)
            return {c["name"].lower(): c.get("change_7d", 0) for c in momentum[:10]}
        except Exception:
            return {}
