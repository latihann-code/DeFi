from defi_agent.backtest.engine import BacktestEngine
from defi_agent.models import PoolData

def test_forced_switching():
    print("🚀 PROVING REALLOCATION LOGIC (Forced Migration)\n")
    engine = BacktestEngine(initial_capital=10000.0)
    
    # Hari 1: Pool A Sangat Bagus (50% APY)
    pool_a = PoolData(pool="A", project="A", chain="ETH", tvl_usd=100_000_000, apy=50.0, underlying_tokens=["USDC"], age_days=100)
    
    print("Step 1: Deposit ke Pool A (50% APY)")
    engine.execute_trade(timestamp=1000, pool=pool_a, action="DEPOSIT", amount=9000)
    
    # Simulasikan data jam berikutnya untuk memicu run_simulation
    print("Step 2: Pool A anjlok ke 2%, Pool B muncul dengan 80% APY...")
    multi_data = {
        "A": [{"timestamp": 5000, "apy": 2.0, "tvl_usd": 100_000_000, "project": "A"}],
        "B": [{"timestamp": 5000, "apy": 80.0, "tvl_usd": 100_000_000, "project": "B"}]
    }
    engine.run_simulation(multi_data, baseline_apy=5.0)
    
    print("\n📝 Final Logs:")
    for log in engine.trade_logs:
        print(f" - {log['action']} {log['pool']} | Reason: {log.get('reason', 'N/A')}")

    has_reallocated = any("Yield Chasing" in str(log.get("reason", "")) for log in engine.trade_logs)
    print(f"\n🏆 REALLOCATION SUCCESS: {'✅ YES' if has_reallocated else '❌ NO'}")

if __name__ == "__main__":
    test_forced_switching()
