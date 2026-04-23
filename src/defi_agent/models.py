from dataclasses import dataclass, field
from typing import List, Dict

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
    apy_spike_24h_percent: float = 0.0 # New: detect abnormal APY jumps
    apy_volatility_penalty: float = 0.0
    inflation_discount: float = 0.0
    
    # New metrics for Meta-Agent
    volatility_index: float = 1.0 # 1.0 = normal, >1.0 = high risk
    audit_score: float = 1.0 # 0.0 to 1.0
    
    # OG Meta Fields
    volume_usd: float = 0.0
    has_points: bool = False
    momentum_score: float = 0.0

@dataclass
class Position:
    pool_id: str
    amount: float
    entry_timestamp: int
    entry_apy: float
