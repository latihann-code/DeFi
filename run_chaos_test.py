from defi_agent.backtest.engine import BacktestEngine
from defi_agent.backtest.interpolator import HourlyInterpolator
import numpy as np

def print_report(name, engine):
    final_equity = engine.get_total_equity()
    # Calculate max drawdown correctly from history
    caps = [p["capital"] for p in engine.portfolio_history]
    peak = caps[0]
    max_dd = 0.0
    for c in caps:
        if c > peak: peak = c
        dd = (peak - c) / peak * 100
        if dd > max_dd: max_dd = dd
        
    print(f"REPORT: {name}")
    print(f" - Final Equity  : ${final_equity:,.2f}")
    print(f" - Max Drawdown  : {max_dd:.2f}%")
    print(f" - Total Trades  : {len(engine.trade_logs)}")
    emergency_count = len([t for p in engine.trade_logs if (t := p).get("emergency")])
    if emergency_count > 0:
        print(f" - 🚨 EMERGENCY EXITS: {emergency_count}")
    print("-" * 30)

def main():
    print("🔥 DeFi Agent: STAGE 2 - REAL CHAOS TESTING 🔥\n")
    
    # Baseline Data: 7 hari, 20% APY
    base_daily = [{"timestamp": 1713657600 + (i * 86400), "apy": 20.0, "tvl_usd": 100_000_000} for i in range(8)]
    
    interpolator = HourlyInterpolator(noise_std=0.0) # No noise for pure event testing
    base_hourly = interpolator.generate_hourly(base_daily, "apy")

    # --- TEST 1: GAS SPIKE ($200) ---
    engine1 = BacktestEngine(initial_capital=10000.0)
    engine1.friction_model.estimate_gas_cost = lambda base_gas_usd: 200.0
    engine1.run_simulation(base_hourly, "pool-1", "Aave")
    print_report("Test 1: Gas Spike Only", engine1)

    # --- TEST 2: APY COLLAPSE (20% -> 1%) ---
    engine2 = BacktestEngine(initial_capital=10000.0)
    collapsed_hourly = [dict(d) for d in base_hourly]
    for d in collapsed_hourly[48:]: d["apy"] = 1.0 
    engine2.run_simulation(collapsed_hourly, "pool-1", "Aave")
    print_report("Test 2: APY Collapse", engine2)

    # --- TEST 3: TVL DROP (30%) - KILL SWITCH ---
    engine3 = BacktestEngine(initial_capital=10000.0)
    bank_run_hourly = [dict(d) for d in base_hourly]
    for d in bank_run_hourly[48:]: 
        d["tvl_usd"] = 60_000_000 
        d["tvl_drop_24h"] = 30.0   
    engine3.run_simulation(bank_run_hourly, "pool-1", "Aave")
    print_report("Test 3: TVL Drop (Kill Switch)", engine3)

    # --- TEST 4: COMBINED CHAOS (THE APOCALYPSE) ---
    engine4 = BacktestEngine(initial_capital=10000.0)
    apocalypse_hourly = [dict(d) for d in base_hourly]
    for d in apocalypse_hourly[48:]:
        d["apy"] = 0.5
        d["tvl_drop_24h"] = 40.0
        d["tvl_usd"] = 50_000_000
    engine4.friction_model.estimate_gas_cost = lambda base_gas_usd: 150.0
    engine4.run_simulation(apocalypse_hourly, "pool-1", "Aave")
    print_report("Test 4: Combined Chaos", engine4)

if __name__ == "__main__":
    main()
