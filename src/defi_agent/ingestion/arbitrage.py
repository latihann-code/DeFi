import logging
import random

logger = logging.getLogger("ArbObserver")

class ArbitrageObserver:
    def __init__(self):
        self.pairs = ["WETH/USDC", "WBTC/USDC", "USDC/DAI"]
        self.dexs = ["Uniswap V3", "Aerodrome"]

    def fetch_mock_prices(self):
        """
        Simulasi fetch harga dari DEX berbeda.
        Nanti diganti pake Web3 call ke Oracle atau Router.
        """
        data = {}
        for pair in self.pairs:
            base_price = 3000.0 if "WETH" in pair else 65000.0 if "WBTC" in pair else 1.0
            # Tambahin noise 0.1% - 0.5% buat simulasi spread
            data[pair] = {
                "Uniswap V3": base_price * (1 + random.uniform(-0.002, 0.002)),
                "Aerodrome": base_price * (1 + random.uniform(-0.002, 0.002))
            }
        return data

    def scan_for_opportunities(self, capital, gas_price_usd=0.01):
        """
        Cek selisih harga dan hitung apakah profit setelah fee.
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

            if spread > 0.001: # Hanya log jika spread > 0.1%
                status = "💰 PROFITABLE" if net_profit > 0 else "❌ NOISE (Loss after fees)"
                logger.info(f"[OBSERVER] {pair} | Spread: {spread*100:.2f}% | {status} | Est. Net: ${net_profit:.4f}")
                
                results.append({
                    "pair": pair,
                    "spread": spread,
                    "net_profit": net_profit
                })
        
        return results
