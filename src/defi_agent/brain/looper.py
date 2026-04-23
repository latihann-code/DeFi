import logging

logger = logging.getLogger("YieldLooper")

class YieldLooperSimulator:
    def __init__(self):
        pass

    def simulate_loop(self, base_apy, borrow_apy, leverage=3.0):
        """
        Menghitung APY bersih jika melakukan looping (leverage).
        Formula: (Base_APY * Leverage) - (Borrow_APY * (Leverage - 1))
        """
        net_apy = (base_apy * leverage) - (borrow_apy * (leverage - 1))
        
        # Risk Assessment: Liquidation threshold
        # Misal LTV Aave 80% (0.8), maka liquidation threshold di leverage 3x sangat mepet.
        risk_level = "HIGH" if leverage >= 2.5 else "MEDIUM" if leverage >= 1.5 else "LOW"
        
        logger.info(f"🌀 [LOOPER] Simulation: Base {base_apy}% | Leverage {leverage}x | Net APY: {net_apy:.2f}% | Risk: {risk_level}")
        return net_apy, risk_level
