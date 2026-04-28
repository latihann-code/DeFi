import pytest
from defi_agent.backtest.engine import BacktestEngine
from defi_agent.models import PoolData

def test_engine_cooldown():
    engine = BacktestEngine(initial_capital=10000)
    
    # Pool data statis
    pool = PoolData(pool="1", project="aave", chain="Ethereum", tvl_usd=100_000_000, apy=50.0, underlying_tokens=["USDC"], age_days=100)
    
    # Trade pertama (Jam ke-0)
    success1 = engine.execute_trade(timestamp=0, pool=pool, action="DEPOSIT", amount=3000)
    assert success1 is True
    
    # Trade kedua di pool yang sama (Jam ke-1) -> Harus GAGAL karena cooldown
    success2 = engine.execute_trade(timestamp=3600, pool=pool, action="DEPOSIT", amount=3000)
    assert success2 is False
    
    # Trade ketiga (setelah 24 jam) -> Harus BERHASIL
    success3 = engine.execute_trade(timestamp=3600*25, pool=pool, action="DEPOSIT", amount=3000)
    assert success3 is True

def test_stage_1_loop():
    engine = BacktestEngine(initial_capital=10000)
    
    # Simulasi 3 jam data pool
    historical_data = [
        {"timestamp": 0, "apy": 10.0, "tvl_usd": 100_000_000},
        {"timestamp": 3600, "apy": 12.0, "tvl_usd": 100_000_000},
        {"timestamp": 7200, "apy": 8.0, "tvl_usd": 100_000_000}
    ]
    
    # Jalankan engine
    engine.run_simulation({"1": historical_data}, baseline_apy=5.0)
    
    # Harusnya ada log transaksi atau update portfolio
    assert len(engine.portfolio_history) > 0

