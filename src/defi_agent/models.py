from dataclasses import dataclass

@dataclass
class PoolData:
    pool: str
    project: str
    chain: str
    tvl_usd: float
    apy: float

    def __init__(self, pool: str, project: str, chain: str, tvlUsd: float, apy: float):
        self.pool = pool
        self.project = project
        self.chain = chain
        self.tvl_usd = tvlUsd
        self.apy = apy
