from defi_agent.models import PoolData
from defi_agent.brain.math_models import calculate_trade_edge

def test_calculate_trade_edge():
    pool = PoolData(
        pool="1", project="aave", chain="Ethereum", tvl_usd=100_000_000, 
        apy=10.0, # 10% Raw APY
        apy_volatility_penalty=2.0, 
        inflation_discount=1.0
    )
    
    capital = 10000.0 # $10k
    days = 7
    
    # Adjusted APY = 10.0 - 2.0 - 1.0 = 7.0%
    # Expected Profit (7 days) = 10000 * 0.07 * (7/365) = 13.424...
    
    # Friction inputs
    token_approval_gas = 1.50
    swap_slippage = 10000 * 0.005 # 0.5% slippage = 50.00
    deposit_gas = 3.00
    withdraw_gas = 3.00
    hidden_costs = 2.00
    
    # Total friction = 1.50 + 50.00 + 3.00 + 3.00 + 2.00 = 59.50
    # Trade Edge = 13.424 - 59.50 = -46.075
    
    edge = calculate_trade_edge(
        pool=pool,
        capital=capital,
        days=days,
        token_approval_gas=token_approval_gas,
        swap_slippage=swap_slippage,
        deposit_gas=deposit_gas,
        withdraw_gas=withdraw_gas,
        hidden_costs=hidden_costs
    )
    
    assert round(edge, 2) == -46.08
