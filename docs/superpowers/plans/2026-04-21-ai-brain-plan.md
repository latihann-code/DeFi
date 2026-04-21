# AI Brain Yield Optimizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the AI Brain's Yield Optimizer module with strict safety filters and advanced edge verification math.

**Architecture:** A new module `defi_agent.brain` containing three core parts: 1) `filters.py` for safety belts, 2) `math_models.py` for the edge verification formula, and 3) `evaluator.py` to tie them together and generate trade signals. Data models will be expanded to support the new metrics.

**Tech Stack:** Python 3.10+, `pytest`

---

### Task 1: Expand Data Models for Advanced Analysis

**Files:**
- Modify: `src/defi_agent/models.py`
- Modify: `tests/test_defillama.py`

- [ ] **Step 1: Write the failing test for expanded PoolData**

```python
# append to tests/test_defillama.py

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src pytest tests/test_defillama.py::test_expanded_pool_data -v`
Expected: FAIL with TypeError about unexpected keyword arguments.

- [ ] **Step 3: Write minimal implementation**

```python
# Modify src/defi_agent/models.py
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

    # We remove the custom __init__ to let dataclass handle defaults properly
```

*Note: You may need to update the `test_pool_data_model` in `tests/test_defillama.py` if the custom `__init__` removal breaks it (e.g. changing `tvlUsd` to `tvl_usd` in test data instantiation).*

```python
# Modify tests/test_defillama.py test_pool_data_model instantiation
    pool = PoolData(
        pool=data["pool"],
        project=data["project"],
        chain=data["chain"],
        tvl_usd=data["tvlUsd"],
        apy=data["apy"]
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src pytest tests/test_defillama.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/defi_agent/models.py tests/test_defillama.py
git commit -m "feat: expand PoolData model with advanced metrics"
```

---

### Task 2: Implement Safety Belt Filters

**Files:**
- Create: `src/defi_agent/brain/__init__.py`
- Create: `src/defi_agent/brain/filters.py`
- Create: `tests/test_filters.py`

- [ ] **Step 1: Write the failing test for safety filters**

```python
# tests/test_filters.py
from defi_agent.models import PoolData
from defi_agent.brain.filters import passes_safety_belts

def test_safety_belts():
    # Good pool
    safe_pool = PoolData(pool="1", project="aave", chain="Ethereum", tvl_usd=60_000_000, apy=10, underlying_tokens=["USDC"], age_days=100, tvl_drop_24h_percent=5)
    assert passes_safety_belts(safe_pool) is True
    
    # TVL too low
    low_tvl = PoolData(pool="2", project="aave", chain="Ethereum", tvl_usd=40_000_000, apy=10, underlying_tokens=["USDC"], age_days=100, tvl_drop_24h_percent=5)
    assert passes_safety_belts(low_tvl) is False
    
    # Not a stablecoin/bluechip
    bad_token = PoolData(pool="3", project="aave", chain="Ethereum", tvl_usd=60_000_000, apy=10, underlying_tokens=["SHIB"], age_days=100, tvl_drop_24h_percent=5)
    assert passes_safety_belts(bad_token) is False
    
    # Too young
    young = PoolData(pool="4", project="aave", chain="Ethereum", tvl_usd=60_000_000, apy=10, underlying_tokens=["USDC"], age_days=30, tvl_drop_24h_percent=5)
    assert passes_safety_belts(young) is False
    
    # Bank run (TVL drop > 20%)
    bank_run = PoolData(pool="5", project="aave", chain="Ethereum", tvl_usd=60_000_000, apy=10, underlying_tokens=["USDC"], age_days=100, tvl_drop_24h_percent=25)
    assert passes_safety_belts(bank_run) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src pytest tests/test_filters.py -v`
Expected: FAIL with ModuleNotFoundError or ImportError

- [ ] **Step 3: Write minimal implementation**

```python
# src/defi_agent/brain/__init__.py
# Empty file

# src/defi_agent/brain/filters.py
from defi_agent.models import PoolData

ALLOWED_TOKENS = {"USDC", "USDT", "DAI", "ETH", "WBTC"}
MIN_TVL = 50_000_000
MIN_AGE_DAYS = 90
MAX_TVL_DROP_PERCENT = 20.0

def passes_safety_belts(pool: PoolData) -> bool:
    if pool.tvl_usd < MIN_TVL:
        return False
        
    if pool.age_days < MIN_AGE_DAYS:
        return False
        
    if pool.tvl_drop_24h_percent > MAX_TVL_DROP_PERCENT:
        return False
        
    # Check if ANY underlying token is NOT in the allowed list
    if not pool.underlying_tokens:
        return False # Reject empty
        
    for token in pool.underlying_tokens:
        if token not in ALLOWED_TOKENS:
            return False
            
    return True
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src pytest tests/test_filters.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/defi_agent/brain/ tests/test_filters.py
git commit -m "feat: implement safety belt filters for AI brain"
```

---

### Task 3: Edge Verification Math Module

**Files:**
- Create: `src/defi_agent/brain/math_models.py`
- Create: `tests/test_math_models.py`

- [ ] **Step 1: Write the failing test for edge calculation**

```python
# tests/test_math_models.py
from defi_agent.models import PoolData
from defi_agent.brain.math_models import calculate_trade_edge

def test_calculate_trade_edge():
    pool = PoolData(
        pool="1", project="aave", chain="Ethereum", tvl_usd=100_000_000, 
        apy=10.0, # 10% Raw APY
        apy_volatility_penalty=2.0, 
        inflation_discount=1.0
    )
    
    capital = 10000.0 # $10k
    days = 7
    
    # Adjusted APY = 10.0 - 2.0 - 1.0 = 7.0%
    # Expected Profit (7 days) = 10000 * 0.07 * (7/365) = 13.424...
    
    # Friction inputs
    token_approval_gas = 1.50
    swap_slippage = 10000 * 0.005 # 0.5% slippage = 50.00
    deposit_gas = 3.00
    withdraw_gas = 3.00
    hidden_costs = 2.00
    
    # Total friction = 1.50 + 50.00 + 3.00 + 3.00 + 2.00 = 59.50
    # Trade Edge = 13.424 - 59.50 = -46.075
    
    edge = calculate_trade_edge(
        pool=pool,
        capital=capital,
        days=days,
        token_approval_gas=token_approval_gas,
        swap_slippage=swap_slippage,
        deposit_gas=deposit_gas,
        withdraw_gas=withdraw_gas,
        hidden_costs=hidden_costs
    )
    
    assert round(edge, 2) == -46.08
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src pytest tests/test_math_models.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Write minimal implementation**

```python
# src/defi_agent/brain/math_models.py
from defi_agent.models import PoolData

def calculate_trade_edge(
    pool: PoolData,
    capital: float,
    days: int,
    token_approval_gas: float,
    swap_slippage: float,
    deposit_gas: float,
    withdraw_gas: float,
    hidden_costs: float
) -> float:
    
    adjusted_apy = pool.apy - pool.apy_volatility_penalty - pool.inflation_discount
    
    net_expected_profit = capital * (adjusted_apy / 100.0) * (days / 365.0)
    
    friction = token_approval_gas + swap_slippage + deposit_gas + withdraw_gas + hidden_costs
    
    trade_edge = net_expected_profit - friction
    return trade_edge
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src pytest tests/test_math_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/defi_agent/brain/math_models.py tests/test_math_models.py
git commit -m "feat: implement edge verification math module"
```

---

### Task 4: The Evaluator (AI Brain Core)

**Files:**
- Create: `src/defi_agent/brain/evaluator.py`
- Create: `tests/test_evaluator.py`

- [ ] **Step 1: Write the failing test for the evaluator**

```python
# tests/test_evaluator.py
from defi_agent.models import PoolData
from defi_agent.brain.evaluator import evaluate_opportunities

def test_evaluate_opportunities():
    good_pool = PoolData(
        pool="good", project="aave", chain="Ethereum", tvl_usd=100_000_000, 
        apy=50.0, underlying_tokens=["USDC"], age_days=100, tvl_drop_24h_percent=0
    )
    
    bad_pool = PoolData( # Fails safety belts (young)
        pool="bad", project="aave", chain="Ethereum", tvl_usd=100_000_000, 
        apy=100.0, underlying_tokens=["USDC"], age_days=10, tvl_drop_24h_percent=0
    )
    
    no_edge_pool = PoolData( # Passes safety, but APY too low to overcome friction
        pool="no_edge", project="aave", chain="Ethereum", tvl_usd=100_000_000, 
        apy=1.0, underlying_tokens=["USDC"], age_days=100, tvl_drop_24h_percent=0
    )
    
    pools = [good_pool, bad_pool, no_edge_pool]
    
    # We pass standard friction assumptions into the evaluator
    signals = evaluate_opportunities(
        pools=pools,
        capital=10000.0,
        days=7,
        token_approval_gas=1.5,
        swap_slippage_percent=0.5, # Evaluator calculates: capital * 0.005
        deposit_gas=3.0,
        withdraw_gas=3.0,
        hidden_costs=2.0
    )
    
    assert len(signals) == 1
    assert signals[0]["action"] == "DEPOSIT"
    assert signals[0]["pool"] == "good"
    assert "trade_edge" in signals[0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src pytest tests/test_evaluator.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Write minimal implementation**

```python
# src/defi_agent/brain/evaluator.py
from typing import List, Dict, Any
from defi_agent.models import PoolData
from defi_agent.brain.filters import passes_safety_belts
from defi_agent.brain.math_models import calculate_trade_edge

def evaluate_opportunities(
    pools: List[PoolData],
    capital: float,
    days: int,
    token_approval_gas: float,
    swap_slippage_percent: float,
    deposit_gas: float,
    withdraw_gas: float,
    hidden_costs: float
) -> List[Dict[str, Any]]:
    
    signals = []
    
    for pool in pools:
        if not passes_safety_belts(pool):
            continue
            
        swap_slippage = capital * (swap_slippage_percent / 100.0)
        
        edge = calculate_trade_edge(
            pool=pool,
            capital=capital,
            days=days,
            token_approval_gas=token_approval_gas,
            swap_slippage=swap_slippage,
            deposit_gas=deposit_gas,
            withdraw_gas=withdraw_gas,
            hidden_costs=hidden_costs
        )
        
        if edge > 0:
            signals.append({
                "action": "DEPOSIT",
                "pool": pool.pool,
                "project": pool.project,
                "asset": pool.underlying_tokens[0] if pool.underlying_tokens else "UNKNOWN",
                "amount": capital,
                "expected_adjusted_apy": pool.apy - pool.apy_volatility_penalty - pool.inflation_discount,
                "trade_edge": edge
            })
            
    return signals
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src pytest tests/test_evaluator.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/defi_agent/brain/evaluator.py tests/test_evaluator.py
git commit -m "feat: implement AI brain evaluator core"
```
