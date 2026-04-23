import logging
from defi_agent.models import PoolData

logger = logging.getLogger("AlphaDiscovery")

class AlphaDiscoveryScanner:
    def __init__(self):
        self.alpha_log = "alpha_discoveries.log"

    def scan_for_alphas(self, pools: list[PoolData]):
        """
        Mencari pool TVL rendah tapi APY tinggi & momentum bagus.
        HANYA UNTUK LOG, bukan untuk dieksekusi main capital.
        """
        alphas = []
        for pool in pools:
            # Filter: TVL $100k - $1M, APY > 100%
            if 100_000 <= pool.tvl_usd < 1_000_000 and pool.apy > 100:
                alphas.append(pool)
                with open(self.alpha_log, "a") as f:
                    f.write(f"{pool.project} on {pool.chain} | APY: {pool.apy}% | TVL: ${pool.tvl_usd:,.0f} | Pair: {pool.underlying_tokens}\n")
                logger.info(f"💎 [ALPHA] Found: {pool.project} ({pool.chain}) | APY: {pool.apy}% | TVL: ${pool.tvl_usd:,.0f}")
        
        return alphas
