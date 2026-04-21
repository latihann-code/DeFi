import random
import numpy as np

class FrictionModel:
    def __init__(self, slippage_factor: float = 0.5):
        """
        :param slippage_factor: Konstanta untuk mengatur seberapa sensitif slippage terhadap likuiditas.
        """
        self.slippage_factor = slippage_factor

    def calculate_slippage(self, capital: float, pool_tvl: float) -> float:
        """
        Menghitung slippage berdasarkan rumus: Slippage ∝ (Capital / Liquidity).
        Asumsi: pool_tvl adalah proxy likuiditas.
        :return: Nilai slippage dalam USD.
        """
        if pool_tvl <= 0:
            return capital # Jika TVL nol, kehilangan semua modal (simulasi ekstrim)
            
        # Rumus dasar: slippage_percent = (Capital / Pool_TVL) * slippage_factor
        # Kita tambahkan basis minimal slippage 0.1% untuk mensimulasikan fee protokol tetap
        slippage_percent = (capital / pool_tvl) * self.slippage_factor + 0.001
        
        return capital * slippage_percent

    def estimate_gas_cost(self, base_gas_usd: float, percentile: str = "P90") -> float:
        """
        Simulasi biaya gas menggunakan percentile (P90) dan lonjakan acak (spike).
        :param base_gas_usd: Estimasi biaya gas rata-rata saat itu.
        :return: Biaya gas yang sudah disesuaikan (USD).
        """
        # P90 berarti kita ambil estimasi yang lebih mahal dari rata-rata
        p90_multiplier = 1.3 # 30% lebih mahal dari base
        
        # Simulasi spike acak (5% kemungkinan terjadi kemacetan jaringan parah)
        if random.random() < 0.05:
            spike_multiplier = random.uniform(2.0, 5.0)
            return base_gas_usd * spike_multiplier
            
        return base_gas_usd * p90_multiplier
