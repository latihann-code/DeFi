import pytest
from defi_agent.backtest.friction import FrictionModel

def test_liquidity_based_slippage():
    model = FrictionModel()
    
    # Pool besar ($100M)
    slippage_big = model.calculate_slippage(capital=10000, pool_tvl=100_000_000)
    
    # Pool kecil ($1M)
    slippage_small = model.calculate_slippage(capital=10000, pool_tvl=1_000_000)
    
    # Pool kecil harus punya slippage lebih besar
    assert slippage_small > slippage_big
    # Nilai slippage harus proporsional terhadap capital/tvl
    assert slippage_big > 0

def test_gas_modeling_p90():
    model = FrictionModel()
    # Simulasi 100 kali untuk mengecek adanya spike sesekali
    gas_costs = [model.estimate_gas_cost(base_gas_usd=10.0) for _ in range(100)]
    
    # Rata-rata harus di atas base karena kita pakai P90
    avg_gas = sum(gas_costs) / len(gas_costs)
    assert avg_gas > 10.0
    
    # Harus ada setidaknya satu spike yang jauh lebih tinggi (misal 2x base)
    assert any(g > 20.0 for g in gas_costs)
