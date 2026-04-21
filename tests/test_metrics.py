import pytest
from defi_agent.backtest.metrics import MetricsCalculator

def test_alpha_calculation():
    calc = MetricsCalculator()
    # Portfolio ROI 10%, Baseline ROI 5%
    portfolio_history = [{"timestamp": 0, "capital": 10000}, {"timestamp": 86400, "capital": 11000}]
    baseline_history = [{"timestamp": 0, "capital": 10000}, {"timestamp": 86400, "capital": 10500}]
    
    alpha = calc.calculate_alpha(portfolio_history, baseline_history)
    assert alpha == 5.0 # (10% - 5%) * 100 = 5.0

def test_drawdown_calculation():
    calc = MetricsCalculator()
    # Capital: 10k -> 12k -> 9k -> 11k
    history = [
        {"capital": 10000},
        {"capital": 12000},
        {"capital": 9000},  # Drop 25% dari peak 12k
        {"capital": 11000}
    ]
    mdd = calc.calculate_max_drawdown(history)
    assert mdd == 25.0

def test_pass_fail_logic():
    calc = MetricsCalculator()
    metrics = {
        "alpha_consistency": 75.0, # Pass (>= 70)
        "max_drawdown": 5.0,        # Pass (<= 10)
        "sharpe_ratio": 1.5,       # Pass (>= 1.0)
        "gas_to_profit_ratio": 20.0 # Pass (<= 40)
    }
    assert calc.evaluate_pass_fail(metrics) is True
    
    # Satu gagal = FAIL
    metrics["max_drawdown"] = 15.0
    assert calc.evaluate_pass_fail(metrics) is False
