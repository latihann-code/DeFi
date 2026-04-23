import logging
from defi_agent.models import PoolData

logger = logging.getLogger("AlphaDiscovery")

class AlphaDiscoveryScanner:
    def __init__(self):
        self.alpha_log = "alpha_discoveries.log"

    def calculate_alpha_score(self, pool: PoolData) -> float:
        """
        Alpha Score (0-100): Menilai seberapa 'berlian' sebuah pool kecil.
        """
        score = 0
        
        # 1. Volume/TVL Ratio (Efisiensi) - Max 40 points
        if pool.tvl_usd > 0:
            vol_ratio = pool.volume_usd / pool.tvl_usd
            score += min(40, vol_ratio * 20) # Ratio 2.0 = 40 pts
            
        # 2. Yield Quality - Max 30 points
        if pool.apy > 500: score += 10 # Terlalu tinggi = Suspect (kecil poinnya)
        elif pool.apy > 100: score += 30 # Sweet spot buat Alpha
        elif pool.apy > 50: score += 20
        
        # 3. Points/Airdrop Bonus - Max 20 points
        if pool.has_points:
            score += 20
            
        # 4. Momentum Score (Dummy for now, will fetch historical soon) - Max 10 points
        score += min(10, pool.momentum_score)
        
        return score

    def scan_for_alphas(self, pools: list[PoolData]):
        """
        Mencari pool TVL rendah ($100k - $1M) dan memberinya skor.
        """
        discoveries = []
        for pool in pools:
            # Filter: Scout range ($100k - $1.5M)
            if 100_000 <= pool.tvl_usd < 1_500_000:
                score = self.calculate_alpha_score(pool)
                
                # Hanya log yang beneran 'berbau' Alpha (Score > 60)
                if score > 60:
                    status = "🏆 HIGH SIGNAL" if score > 80 else "🔍 INTERESTING"
                    discovery = {
                        "project": pool.project,
                        "chain": pool.chain,
                        "apy": pool.apy,
                        "tvl": pool.tvl_usd,
                        "score": score,
                        "status": status
                    }
                    discoveries.append(discovery)
                    
                    with open(self.alpha_log, "a") as f:
                        f.write(f"[{status}] Score: {score:.1f} | {pool.project} ({pool.chain}) | APY: {pool.apy}% | TVL: ${pool.tvl_usd:,.0f}\n")
                    
                    logger.info(f"💎 [ALPHA] {status} | {pool.project} ({pool.chain}) | Score: {score:.1f}")
        
        return sorted(discoveries, key=lambda x: x["score"], reverse=True)
