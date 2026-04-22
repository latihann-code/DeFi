from defi_agent.backtest.engine import BacktestEngine
from defi_agent.backtest.interpolator import HourlyInterpolator

def main():
    print("🧠 DeFi Meta-Agent: ANTICIPATORY 'SMELL TEST' DEMO")
    print("Scenario: The Honey Pot Trap (APY Spike before Rugpull)\n")
    
    # 1. SETUP DATA (72 jam)
    # Jam 0-24: Normal (APY 20%, TVL $100M)
    # Jam 25-48: APY Spike to 80%, TVL stays same (SMELL TEST TRIGGER)
    # Jam 49-72: REAL RUGPULL (TVL drops 90%)
    
    hourly_data = []
    start_ts = 1713657600
    
    for h in range(73):
        ts = start_ts + (h * 3600)
        apy = 200.0
        tvl = 100_000_000
        apy_spike = 0.0
        tvl_drop = 0.0
        
        if 24 < h <= 48:
            apy = 500.0
            apy_spike = 300.0 # Extreme spike
        elif h > 48:
            apy = 1.0
            tvl = 10_000_000 # RUGPULL!
            tvl_drop = 90.0
            
        hourly_data.append({
            "timestamp": ts,
            "apy": apy,
            "tvl_usd": tvl,
            "apy_spike_24h": apy_spike,
            "tvl_drop_24h": tvl_drop
        })
        
    # 2. RUN ENGINE
    engine = BacktestEngine(initial_capital=100000.0, cooldown_hours=0) # No cooldown for demo speed
    multi_data = {"honey-pot-pool": hourly_data}
    
    print("⚙️ Running simulation...")
    engine.run_simulation(multi_data, baseline_apy=5.0)
    
    # 3. ANALYSIS
    print("-" * 45)
    print(f"Final Capital   : ${engine.get_total_equity():,.2f}")
    print(f"Total Trades    : {len(engine.trade_logs)}")
    
    print("\n📝 Execution Timeline & Decisions:")
    for log in engine.trade_logs:
        h_idx = (log['ts'] - start_ts) // 3600
        reason = log.get('reason', 'N/A')
        print(f" - Hour {h_idx:02d}: {log['act']} | Reason: {reason}")
        
    # Check if we survived
    if engine.get_total_equity() > 9000:
        print("\n✅ SURVIVAL SUCCESS: Bot exited BEFORE the rugpull thanks to the Smell Test!")
    else:
        print("\n❌ FAILED: Bot got rekt.")

if __name__ == "__main__":
    main()
