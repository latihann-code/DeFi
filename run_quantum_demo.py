from defi_agent.backtest.engine import BacktestEngine
from defi_agent.models import PoolData

def main():
    print("🏛️ DeFi Meta-Agent: QUANTITATIVE PORTFOLIO DEMO\n")
    
    engine = BacktestEngine(initial_capital=10000.0)
    
    # Data Jam ke-0
    # Pool Safe (Aave)
    safe_pool = PoolData(pool="safe", project="Aave", chain="ETH", tvl_usd=500_000_000, apy=10.0, age_days=500)
    # Pool Degen (New Farm)
    degen_pool = PoolData(pool="degen", project="NewFarm", chain="ETH", tvl_usd=5_000_000, apy=120.0, age_days=10)
    
    multi_data = {
        "safe": [{"timestamp": 1000, "apy": 10.0, "tvl_usd": 500_000_000}],
        "degen": [{"timestamp": 1000, "apy": 120.0, "tvl_usd": 5_000_000}]
    }
    
    print("Step 1: Running Meta-Strategy...")
    engine.run_simulation(multi_data, baseline_apy=5.0)
    
    print("-" * 40)
    print(f"Total Equity: ${engine.get_total_equity():,.2f}")
    print(f"Idle Cash   : ${engine.idle_cash:,.2f}")
    
    print("\n📊 Active Positions:")
    for p_id, pos in engine.positions.items():
        weight = (pos.amount / engine.get_total_equity()) * 100
        print(f" - {p_id}: ${pos.amount:,.2f} ({weight:.1f}% of portfolio)")
    
    print("\n📝 Logic Explanation:")
    print("Bot membagi modal: Porsi besar ke Safe karena EV stabil,")
    print("Porsi kecil ke Degen karena APY tinggi tapi probabilitas fail tinggi.")

if __name__ == "__main__":
    main()
