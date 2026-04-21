# AI Brain: Yield Optimizer (Phase 1) - Design Specification

## Overview
This specification details the AI Brain's first operational module: The **Yield Optimizer**. We are adopting a "Hybrid B" approach (Quantitative Data + Strict Rules-Based Safety Belts). The goal is to build a reliable, slow-but-steady profit engine focused entirely on Yield Farming (Lending & Liquidity Provisioning), deliberately avoiding the ultra-low latency, high-infrastructure requirements of MEV/Arbitrage games for this phase.

## Core Philosophy: Survive First, Profit Second
In the DeFi "Dark Forest," minimizing losses from hacks, de-pegs, and extreme gas fees is more important than chasing the highest APY. The AI will operate with extreme prejudice against risk.

## 1. Input Data (From Data Ingestion Engine)
The AI Brain will consume:
- `List[PoolData]`: Current APY, TVL, Project Name, Chain (from DefiLlama).
- `Historical Chart Data`: Past 30-day APY and TVL trends to determine stability.
- `Gas Oracle Data (Future/Mocked)`: Current estimated network transaction costs.

## 2. The "Safety Belt" Filters (Hard Rules)
Before any yield opportunity is even considered for mathematical evaluation, it MUST pass these strict filters:
*   **The TVL Floor:** Protocol TVL must be > $50,000,000. (Eliminates micro-cap rug pulls).
*   **The Asset Whitelist:** Initially, only evaluate pools containing `Stablecoins (USDC, USDT, DAI)` or `Bluechips (ETH, WBTC)`. (Eliminates Impermanent Loss from volatile altcoins).
*   **The Age Rule (Lindy Effect):** The protocol must have existed and maintained TVL for at least 90 days.
*   **The "Bank Run" Trigger (Stop-Loss):** If a protocol's TVL drops by > 20% in a 24-hour period, it triggers an immediate "Emergency Withdraw" signal, regardless of gas fees.

## 3. The Edge Verification Engine (Math Module)
If a pool passes the Safety Belts, the AI calculates the true profitability of moving funds.

**The Formula:**
`Net Expected Profit (N days) = (Capital * APY_Difference * (N / 365))`
`Friction = (Swap Slippage) + (Deposit Gas Fee) + (Withdraw Gas Fee)`
`Trade Edge = Net Expected Profit - Friction`

**The Execution Rule:**
The AI will only generate a "Move Funds" signal if `Trade Edge > 0` assuming a conservative time horizon (e.g., $N = 7$ days). It must pay for its own gas within a week.

## 4. Backtesting & Friction Simulator (The Proving Ground)
To prove this logic works without risking real capital, the Backtester will simulate trades against historical data with forced pessimism:
*   **Gas Pessimism:** Assumes the highest gas fee of the day for the simulated transaction.
*   **Slippage Pessimism:** Assumes a flat 0.5% loss on every simulated swap/deposit into a pool.
*   **Baseline Comparison:** The tracker will plot the AI's "Yield Portfolio" against a "Hold 100% USDC in Aave" passive baseline. The AI must beat the baseline after all simulated friction.

## 5. Output / Action
*   **Signal Generation:** Produces a JSON object: `{"action": "DEPOSIT", "protocol": "Aave V3", "asset": "USDC", "amount": 10000, "expected_apy": 8.5, "estimated_gas": 15.00}`.
*   In Paper Trading mode, this signal updates the Virtual Portfolio database.