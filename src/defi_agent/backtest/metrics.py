import numpy as np

class MetricsCalculator:
    def calculate_alpha(self, portfolio_history: list[dict], baseline_history: list[dict]) -> float:
        """
        Menghitung ROI Alpha (selisih ROI portfolio vs baseline dalam persen).
        """
        if not portfolio_history or not baseline_history:
            return 0.0
            
        p_start = portfolio_history[0]["capital"]
        p_end = portfolio_history[-1]["capital"]
        p_roi = (p_end - p_start) / p_start
        
        b_start = baseline_history[0]["capital"]
        b_end = baseline_history[-1]["capital"]
        b_roi = (b_end - b_start) / b_start
        
        return (p_roi - b_roi) * 100

    def calculate_max_drawdown(self, portfolio_history: list[dict]) -> float:
        """
        Menghitung penurunan terdalam dari puncak (Maximum Drawdown) dalam persen.
        """
        if not portfolio_history:
            return 0.0
            
        capitals = [p["capital"] for p in portfolio_history]
        peak = capitals[0]
        max_dd = 0.0
        
        for cap in capitals:
            if cap > peak:
                peak = cap
            dd = (peak - cap) / peak
            if dd > max_dd:
                max_dd = dd
        
        return max_dd * 100

    def calculate_sharpe_ratio(self, returns: list[float], risk_free_rate: float = 0.0) -> float:
        """
        Menghitung Sharpe Ratio berdasarkan rata-rata return vs volatilitas.
        """
        if not returns:
            return 0.0
        avg_return = np.mean(returns)
        std_dev = np.std(returns)
        if std_dev == 0:
            return 0.0
        return (avg_return - risk_free_rate) / std_dev

    def evaluate_pass_fail(self, metrics: dict) -> bool:
        """
        Sistem PASS/FAIL berdasarkan Syarat Mati:
        - Alpha consistency >= 70
        - Max Drawdown <= 10
        - Sharpe Ratio >= 1.0
        - Gas-to-Profit <= 40
        """
        checks = [
            metrics.get("alpha_consistency", 0) >= 70,
            metrics.get("max_drawdown", 100) <= 10,
            metrics.get("sharpe_ratio", 0) >= 1.0,
            metrics.get("gas_to_profit_ratio", 100) <= 40
        ]
        return all(checks)
