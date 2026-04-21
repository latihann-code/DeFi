from dataclasses import dataclass, field
from typing import List

@dataclass
class PoolData:
    pool: str
    project: str
    chain: str
    tvl_usd: float
    apy: float
    underlying_tokens: List[str] = field(default_factory=list)
    age_days: int = 0
    tvl_drop_24h_percent: float = 0.0
    apy_volatility_penalty: float = 0.0
    inflation_discount: float = 0.0
