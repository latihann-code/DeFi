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

## 2. The "Safety Belt" Filters (Adjustable Rules)
Before any yield opportunity is even considered for mathematical evaluation, it MUST pass these filters. *Note: These are initial conservative parameters that can be adjusted later as the AI's risk modeling improves.*
*   **The TVL Floor:** Protocol TVL must be > $50,000,000 initially. (Eliminates micro-cap rug pulls, but adjustable for higher-risk strategies later).
*   **The Asset Whitelist:** Initially, only evaluate pools containing `Stablecoins (USDC, USDT, DAI)` or `Bluechips (ETH, WBTC)`.
*   **The Age Rule (Lindy Effect):** The protocol must have existed and maintained TVL for at least 90 days.
*   **The "Bank Run" Trigger (Stop-Loss):** If a protocol's TVL drops by > 20% in a 24-hour period, it triggers an immediate "Emergency Withdraw" signal, regardless of gas fees.

## 3. The Edge Verification Engine (Math Module)
If a pool passes the Safety Belts, the AI calculates the true profitability of moving funds.

**The Formula (Advanced):**
`Adjusted_APY = Raw_APY - APY_Volatility_Penalty - Reward_Token_Inflation_Discount`
*(If the yield comes from a highly volatile farm token, the APY is heavily discounted to reflect reality).*

`Net Expected Profit (N days) = (Capital * Adjusted_APY * (N / 365))`

`Friction = (Token Approval Gas) + (Swap Slippage) + (Deposit Gas) + (Withdraw Gas) + (Hidden Costs)`
*(Hidden costs include: Bridge fees/risks, Withdrawal delays/lock-up periods, and the Opportunity Cost of locked capital).*

`Trade Edge = Net Expected Profit - Friction`

**The Execution Rule:**
The AI will only generate a "Move Funds" signal if `Trade Edge > 0` assuming a conservative time horizon (e.g., $N = 7$ days). It must pay for its own gas and hidden costs within a week.

## 4. Backtesting & Friction Simulator (The Proving Ground)
To prove this logic works without risking real capital, the Backtester will simulate trades against historical data with forced pessimism:
*   **Gas Pessimism:** Assumes the highest gas fee of the day for the simulated transaction.
*   **Slippage Pessimism:** Assumes a flat 0.5% loss on every simulated swap/deposit into a pool.
*   **Multi-Baseline Evaluation:** The tracker will plot the AI's "Yield Portfolio" against THREE strict passive baselines to prove true alpha:
    1.  **Hold Cash:** Zero risk, zero yield baseline.
    2.  **Hold Aave USDC:** Safe, passive yield baseline.
    3.  **Hold ETH:** Market momentum baseline.
    *The AI MUST consistently beat at least the "Hold Aave USDC" baseline after all friction to be considered viable.*

## 5. Output / Action
*   **Signal Generation:** Produces a JSON object: `{"action": "DEPOSIT", "protocol": "Aave V3", "asset": "USDC", "amount": 10000, "expected_apy": 8.5, "estimated_gas": 15.00}`.
*   In Paper Trading mode, this signal updates the Virtual Portfolio database.