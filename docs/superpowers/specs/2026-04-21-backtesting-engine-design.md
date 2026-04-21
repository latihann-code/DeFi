# DeFi Agent Backtesting Engine (The Proving Ground) - Design Specification

## Overview
This specification outlines the design for the **Backtesting Engine**, the core validation layer of the DeFi AI Agent. Its purpose is to prove a strategy's edge (Alpha) and survival capability (Robustness) before any real capital is deployed. The engine uses a **Two-Stage Validation Pipeline (Mode F)** to separate normal performance from extreme event resilience.

## 1. Validation Pipeline (Mode F)
The engine executes backtests in two sequential stages:
*   **Stage 1: Historical Replay (Clean Signal Test):** Validates if the AI Brain can generate profit in "normal" market conditions using historical daily data interpolated to hourly granularity.
*   **Stage 2: Stress-Tester (Survival Test):** Injects "Synthetic Events" (Bank Runs, De-pegs, Gas Spikes) into the Stage 1 timeline to test the agent's risk management and "panic" logic.

## 2. Data Modeling & Granularity (Mode D2)
To balance simulation speed and realism, the engine uses **Hybrid Adaptive Granularity**:
*   **Base Loop (Hourly):** Standard simulation frequency using **Linear Interpolation + Gaussian Noise**. (Spline interpolation is strictly avoided as it over-smooths volatility).
*   **Event Trigger (Instant):** If a significant change in TVL or APY is detected, the simulator triggers an immediate re-evaluation step.
*   **Synthetic Event Injection:** Randomly or based on known historical crises (e.g., USDC de-peg, March 2023), the engine "injects" extreme volatility to test the agent's reaction.

## 3. Decision Thresholds (Mode D3) & Execution Rules
The simulator evaluates the agent's decisions based on **Hybrid Adaptive Thresholds** and strict execution logic:
*   **Statistical (Core):** Triggers an evaluation if `Current Change > k * Historical Std Dev`.
*   **Tiered Sensitivity:** Stablecoin pools have tighter thresholds (e.g., 1.5σ) compared to blue-chip pools (2σ).
*   **Absolute Panic Floor:** Hard rules (e.g., TVL drop > 20% in 24h) trigger immediate withdrawal signals regardless of other factors.
*   **Trade Cooldown:** To prevent spamming and fake profits, the agent MUST wait for a **Cooldown Period (6–24 hours)** after every executed trade before initiating a new one in the same pool.
*   **Minimum Edge Margin:** Instead of `Edge > 0`, the agent only signals a trade if `Expected Profit > Friction * 1.5`. This provides a safety margin for unmodeled slippage/latency.

## 4. Friction & Execution Modeling
The engine implements a **Realistic Friction Simulator**:
*   **Gas Modeling:** Uses **P75–P90 Percentile Gas** prices from the simulated day, with occasional random "spike events" to simulate network congestion. (Highest-of-day is avoided as too extreme, but P90 ensures conservatism).
*   **Liquidity-Based Slippage:** Slippage is modeled as `Slippage ∝ 1 / Liquidity (TVL Proxy)`. Larger pools have lower slippage; smaller pools penalize large trades heavily.
*   **Hidden Costs:** Models token approval costs, withdrawal delays (lock-ups), and capital opportunity costs.

## 5. Evaluation Metrics (The "Hard Gates")
A strategy must produce an explicit **PASS/FAIL** output. It is only considered viable if it passes all "Hard Gates":
1.  **Alpha Consistency (PASS/FAIL):** `Net Alpha vs Baseline > 0` in ≥ 70% of periods.
2.  **Survival Rule (PASS/FAIL):** `Maximum Drawdown ≤ 10%` (for stablecoins) and `Emergency Success Rate ≥ 80%`.
3.  **Profit Quality (PASS/FAIL):** `Sharpe Ratio ≥ 1.0` and `Profit Factor ≥ 1.5`.
4.  **Efficiency (PASS/FAIL):** `Gas-to-Profit Ratio ≤ 40%`.
5.  **No-Trade Discipline (PASS/FAIL):** Remains idle for ≥ 20% of simulation time.

**If ANY gate fails, the final result is a FAIL.**


## 6. Baselines for Comparison
Performance is plotted against three strict baselines:
*   **Baseline 1 (Hold Cash):** Risk-free, zero-yield baseline.
*   **Baseline 2 (Hold Aave USDC):** Safe, passive yield benchmark.
*   **Baseline 3 (Hold ETH):** Market momentum benchmark.

## 7. Implementation Units
*   `defi_agent.backtest.interpolator`: Logic to turn daily data into hourly snapshots.
*   `defi_agent.backtest.engine`: The main simulation loop (Mode F).
*   `defi_agent.backtest.friction`: Real-world cost modeling (Gas, Slippage).
*   `defi_agent.backtest.metrics`: Calculator for Sharpe, Drawdown, and Alpha.
