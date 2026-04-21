# Data Ingestion Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the foundational Data Ingestion module to fetch real-time yields and protocol data from DefiLlama, enabling rigorous backtesting.

**Architecture:** A clean Python module `defi_agent.ingestion` with dedicated clients for external APIs (starting with DefiLlama). It includes robust error handling and data parsing to ensure downstream AI strategies receive structured, reliable data. We will use `pytest` and `responses` to mock the APIs during testing.

**Tech Stack:** Python 3.10+, `requests`, `pytest`, `responses`

---

### Task 1: Project Setup and Dependencies

**Files:**
- Create: `requirements.txt`
- Create: `pytest.ini`

- [ ] **Step 1: Create requirements.txt**

```text
requests==2.31.0
pytest==8.1.1
responses==0.25.0
```

- [ ] **Step 2: Create pytest.ini for testing configuration**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
```

- [ ] **Step 3: Commit**

```bash
git add requirements.txt pytest.ini
git commit -m "chore: setup project dependencies and test config"
```

---

### Task 2: DefiLlama Client Skeleton and Yield Data Model

**Files:**
- Create: `src/defi_agent/__init__.py`
- Create: `src/defi_agent/models.py`
- Create: `src/defi_agent/ingestion/__init__.py`
- Create: `src/defi_agent/ingestion/defillama.py`
- Create: `tests/test_defillama.py`

- [ ] **Step 1: Write the failing test for data models**

```python
# tests/test_defillama.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_defillama.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'defi_agent'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/defi_agent/__init__.py
# Empty file

# src/defi_agent/ingestion/__init__.py
# Empty file

# src/defi_agent/models.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src pytest tests/test_defillama.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/ tests/
git commit -m "feat: add defi_agent module structure and PoolData model"
```

---

### Task 3: Implement DefiLlama Yield Fetching

**Files:**
- Modify: `src/defi_agent/ingestion/defillama.py`
- Modify: `tests/test_defillama.py`

- [ ] **Step 1: Write the failing test for fetching pools**

```python
# append to tests/test_defillama.py
import responses
from defi_agent.ingestion.defillama import DefiLlamaClient

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src pytest tests/test_defillama.py::test_fetch_yields -v`
Expected: FAIL with "ImportError: cannot import name 'DefiLlamaClient' from 'defi_agent.ingestion.defillama'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/defi_agent/ingestion/defillama.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src pytest tests/test_defillama.py::test_fetch_yields -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/defi_agent/ingestion/defillama.py tests/test_defillama.py
git commit -m "feat: implement DefiLlamaClient to fetch and parse yield pools"
```

---

### Task 4: Error Handling and Edge Cases

**Files:**
- Modify: `src/defi_agent/ingestion/defillama.py`
- Modify: `tests/test_defillama.py`

- [ ] **Step 1: Write the failing test for API errors**

```python
# append to tests/test_defillama.py
import requests

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src pytest tests/test_defillama.py::test_fetch_yields_api_error -v`
Expected: FAIL with "requests.exceptions.HTTPError: 500 Server Error"

- [ ] **Step 3: Write minimal implementation**

```python
# Modify src/defi_agent/ingestion/defillama.py -> fetch_yields method
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src pytest tests/test_defillama.py::test_fetch_yields_api_error -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/defi_agent/ingestion/defillama.py tests/test_defillama.py
git commit -m "fix: handle API errors gracefully in DefiLlamaClient"
```
