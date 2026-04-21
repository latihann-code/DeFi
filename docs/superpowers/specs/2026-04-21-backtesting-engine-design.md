# DeFi Agent Backtesting Engine (The Proving Ground) - Design Specification

## Overview
This specification outlines the design for the **Backtesting Engine**, the core validation layer of the DeFi AI Agent. Its purpose is to prove a strategy's edge (Alpha) and survival capability (Robustness) before any real capital is deployed. The engine uses a **Two-Stage Validation Pipeline (Mode F)** to separate normal performance from extreme event resilience.

## 1. Validation Pipeline (Mode F)
The engine executes backtests in two sequential stages:
*   **Stage 1: Historical Replay (Clean Signal Test):** Validates if the AI Brain can generate profit in "normal" market conditions using historical daily data interpolated to hourly granularity.
*   **Stage 2: Stress-Tester (Survival Test):** Injects "Synthetic Events" (Bank Runs, De-pegs, Gas Spikes) into the Stage 1 timeline to test the agent's risk management and "panic" logic.

## 2. Data Modeling & Granularity (Mode D2)
To balance simulation speed and realism, the engine uses **Hybrid Adaptive Granularity**:
*   **Base Loop (Hourly):** Standard simulation frequency using linear/spline interpolation of DefiLlama's daily snapshots.
*   **Event Trigger (Instant):** If a significant change in TVL or APY is detected, the simulator triggers an immediate re-evaluation step.
*   **Synthetic Event Injection:** Randomly or based on known historical crises (e.g., USDC de-peg, March 2023), the engine "injects" extreme volatility to test the agent's reaction.

## 3. Decision Thresholds (Mode D3)
The simulator evaluates the agent's decisions based on **Hybrid Adaptive Thresholds**:
*   **Statistical (Core):** Triggers an evaluation if `Current Change > k * Historical Std Dev`.
*   **Tiered Sensitivity:** Stablecoin pools have tighter thresholds (e.g., 1.5σ) compared to blue-chip pools (2σ).
*   **Absolute Panic Floor:** Hard rules (e.g., TVL drop > 20% in 24h) trigger immediate withdrawal signals regardless of other factors.

## 4. Friction & Execution Modeling
The engine implements a **Pessimistic Friction Simulator**:
*   **Gas Modeling:** Uses a "Highest-of-Day" gas fee assumption for every transaction to avoid over-optimistic ROI.
*   **Slippage:** Implements a flat 0.5% slippage/swap fee penalty for every simulated trade.
*   **Hidden Costs:** Models token approval costs, withdrawal delays (lock-ups), and capital opportunity costs.

## 5. Evaluation Metrics (The "Hard Gates")
A strategy is only considered viable if it passes all five "Hard Gates":
1.  **Alpha Consistency:** `Net Alpha vs Baseline > 0` in ≥ 70% of the simulated periods.
2.  **Survival Rule:** `Maximum Drawdown ≤ 10%` for stablecoin strategies.
3.  **Profit Quality:** `Sharpe Ratio ≥ 1.0` and `Profit Factor ≥ 1.5`.
4.  **Efficiency:** `Gas-to-Profit Ratio ≤ 40%`.
5.  **No-Trade Discipline:** The system must remain idle (No-Trade) for ≥ 20% of the simulation time to avoid overtrading.

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
