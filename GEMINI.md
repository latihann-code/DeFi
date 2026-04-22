# DeFi Agent: Yield Optimization & Execution System

This project is a quantitative DeFi yield optimization platform capable of market data ingestion, risk-adjusted opportunity evaluation, strategy backtesting, and on-chain execution.

## Tech Stack
- **Language:** Python 3.10+
- **Blockchain:** `web3.py` (EIP-1559 support)
- **Data/Math:** `numpy`, standard library `math`
- **Testing:** `pytest`
- **APIs:** DefiLlama (via `requests`)

## Core Architecture

### 1. Ingestion (`src/defi_agent/ingestion/`)
Handles fetching market data. Currently supports DefiLlama for TVL and APY data.
- **Key Symbol:** `DefiLlamaClient`

### 2. Brain (`src/defi_agent/brain/`)
The quantitative core. Evaluates pools based on risk factors (TVL, Protocol Age, Volatility) and Expected Value (EV).
- **Key Symbols:** `calculate_risk_score`, `calculate_expected_value`, `YieldEvaluator`

### 3. Execution (`src/defi_agent/execution/`)
Manages on-chain interactions.
- **Adapters:** Protocol-specific logic (e.g., Aave V3) inheriting from `BaseAdapter`.
- **Manager:** `TransactionManager` handles nonces, gas (EIP-1559), and signing.

### 4. Backtest (`src/defi_agent/backtest/`)
Simulates strategies against historical or synthetic data.

## Development Mandates

### Architecture & Patterns
- **Models:** Use `dataclasses` for data structures (`src/defi_agent/models.py`).
- **Extensibility:** Use Abstract Base Classes (`ABC`) for new execution adapters.
- **Safety:** Always implement `dry_run` or simulation modes for execution logic.

### Testing
- **Framework:** `pytest`.
- **Requirements:** Every new feature or bug fix MUST include a corresponding test.
- **Chaos Testing:** Use `run_chaos_test.py` to validate system resilience under volatile conditions.

### Security
- **Credentials:** NEVER hardcode private keys or RPC URLs. Use environment variables.
- **Simulation:** Validate transaction encoding via `dry_run` before sending to `TransactionManager`.

## Project Workflows
- **Demoing:** Use `run_demo.py` for basic simulation and `run_pro_demo.py` for advanced scenarios.
- **Backtesting:** Use `src/defi_agent/backtest/engine.py` to run historical simulations.
