import logging
import random

logger = logging.getLogger("ArbObserver")

class ArbitrageObserver:
    def __init__(self):
        # Scout Mode: Monitor Top 10 Volume Pairs
        self.pairs = [
            "WETH/USDC", "WBTC/USDC", "USDC/USDT", "ETH/DAI",
            "ARB/USDC", "OP/USDC", "LINK/USDC", "SOL/USDC",
            "PEPE/WETH", "AERO/USDC"
        ]
        self.dexs = ["Uniswap V3", "Aerodrome"]

    def fetch_mock_prices(self):
        """
        Simulasi fetch harga dari DEX berbeda dengan noise realistis.
        """
        data = {}
        for pair in self.pairs:
            base_price = 3000.0 if "ETH" in pair else 65000.0 if "BTC" in pair else 1.0
            if "ARB" in pair: base_price = 1.2
            if "OP" in pair: base_price = 2.5
            if "PEPE" in pair: base_price = 0.000008
            
            # Spread 0.1% - 0.8%
            data[pair] = {
                "Uniswap V3": base_price * (1 + random.uniform(-0.004, 0.004)),
                "Aerodrome": base_price * (1 + random.uniform(-0.004, 0.004))
            }
        return data

    def scan_for_opportunities(self, capital, gas_price_usd=0.01):
        """
        Scout Mode: Deteksi Arbitrase di Top Pairs.
        """
        prices = self.fetch_mock_prices()
        results = []

        for pair, dex_prices in prices.items():
            p1 = dex_prices["Uniswap V3"]
            p2 = dex_prices["Aerodrome"]
            
            spread = abs(p1 - p2) / min(p1, p2)
            gross_profit = capital * spread
            
            # Fee estimasi: 0.3% per swap x 2 DEX = 0.6%
            dex_fees = capital * 0.006
            net_profit = gross_profit - dex_fees - gas_price_usd

            # Log significant signals
            if spread > 0.005: # > 0.5% Spread
                status = "💰 PROFITABLE" if net_profit > 0 else "❌ NOISE (Low Capital)"
                logger.info(f"[SCOUT] {pair} | Spread: {spread*100:.2f}% | {status} | Est. Net: ${net_profit:.4f}")
                
                results.append({
                    "pair": pair,
                    "spread": spread,
                    "net_profit": net_profit
                })
        
        return results
