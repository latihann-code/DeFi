# tests/test_evaluator.py
from defi_agent.models import PoolData
from defi_agent.brain.evaluator import evaluate_opportunities

def test_evaluate_opportunities():
    good_pool = PoolData(
        pool="good", project="aave", chain="Ethereum", tvl_usd=100_000_000, 
        apy=50.0, underlying_tokens=["USDC"], age_days=100, tvl_drop_24h_percent=0
    )
    
    bad_pool = PoolData( # Fails safety belts (young)
        pool="bad", project="aave", chain="Ethereum", tvl_usd=100_000_000, 
        apy=100.0, underlying_tokens=["USDC"], age_days=10, tvl_drop_24h_percent=0
    )
    
    no_edge_pool = PoolData( # Passes safety, but APY too low to overcome friction
        pool="no_edge", project="aave", chain="Ethereum", tvl_usd=100_000_000, 
        apy=1.0, underlying_tokens=["USDC"], age_days=100, tvl_drop_24h_percent=0
    )
    
    pools = [good_pool, bad_pool, no_edge_pool]
    
    # We pass standard friction assumptions into the evaluator
    signals = evaluate_opportunities(
        pools=pools,
        capital=10000.0,
        days=7,
        token_approval_gas=1.5,
        swap_slippage_percent=0.5, # Evaluator calculates: capital * 0.005
        deposit_gas=3.0,
        withdraw_gas=3.0,
        hidden_costs=2.0
    )
    
    assert len(signals) == 1
    assert signals[0]["action"] == "DEPOSIT"
    assert signals[0]["pool"] == "good"
    assert "trade_edge" in signals[0]
