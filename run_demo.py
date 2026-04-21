from defi_agent.models import PoolData
from defi_agent.backtest.interpolator import HourlyInterpolator
from defi_agent.backtest.engine import BacktestEngine
from defi_agent.backtest.metrics import MetricsCalculator

def run_realistic_simulation():
    print("🚀 DeFi Agent: FULL PROFIT SIMULATION (1 Month Run)\n")
    
    # 1. SETUP DATA HISTORIS (30 Hari)
    # Kita buat data harian: 30 hari dengan yield 20%
    daily_data = []
    start_ts = 1713657600
    for i in range(31):
        daily_data.append({
            "timestamp": start_ts + (i * 86400),
            "apy": 20.0, # 20% APY stabil
            "tvl_usd": 100_000_000
        })
    
    # 2. INTERPOLASI KE HOURLY
    interpolator = HourlyInterpolator(noise_std=0.5)
    hourly_data = interpolator.generate_hourly(daily_data, "apy")
    
    # 3. RUN ENGINE (Dengan Profit Accrual & Baseline)
    # Modal $10k, Baseline Aave USDC (5% APY)
    engine = BacktestEngine(initial_capital=10000.0)
    engine.run_simulation(hourly_data, pool_id="aave-v3", project="Aave", baseline_apy=5.0)
    
    # 4. METRICS CALCULATION
    calc = MetricsCalculator()
    alpha = calc.calculate_alpha(engine.portfolio_history, engine.portfolio_history) # Dummy baseline context
    
    # Custom calculation for Equity Curve vs Baseline
    final_p = engine.get_total_equity()
    final_b = engine.portfolio_history[-1]["baseline"]
    net_profit = final_p - engine.initial_capital
    alpha_vs_baseline = ((final_p / final_b) - 1) * 100
    
    print("-" * 40)
    print(f"Initial Capital   : ${engine.initial_capital:,.2f}")
    print(f"Final Capital     : ${final_p:,.2f}")
    print(f"Final Baseline    : ${final_b:,.2f}")
    print("-" * 40)
    print(f"Net Profit (USD)  : ${net_profit:,.2f}")
    print(f"Alpha vs Baseline : {alpha_vs_baseline:+.4f}%")
    print(f"Total Trades      : {len(engine.trade_logs)}")
    print("-" * 40)

if __name__ == "__main__":
    run_realistic_simulation()
