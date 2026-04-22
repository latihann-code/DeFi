import json
import logging
from typing import List, Dict
from defi_agent.ingestion.defillama import DefiLlamaClient
from defi_agent.models import PoolData

logger = logging.getLogger("MultiChainScanner")

class MultiChainScanner:
    def __init__(self, chains_config_path: str = "chains.json"):
        with open(chains_config_path, 'r') as f:
            self.chains = json.load(f)
        self.client = DefiLlamaClient()
        # Estimasi biaya bridge rata-rata (USD)
        self.bridge_fee_estimate = 1.5 

    def scan_all_chains(self) -> Dict[str, List[PoolData]]:
        """
        Narik data pool untuk semua chain yang ada di config.
        """
        logger.info(f"📡 Scanning yields for {len(self.chains)} chains...")
        all_yields = self.client.fetch_yields()
        
        results = {chain_id: [] for chain_id in self.chains.keys()}
        
        for pool in all_yields:
            # DefiLlama pake nama chain (misal: 'Arbitrum', 'Base')
            # Kita mapping ke key config kita
            chain_name_lower = pool.chain.lower()
            if chain_name_lower in results:
                results[chain_name_lower].append(pool)
            elif chain_name_lower == "ethereum": # Handle alias
                 results["ethereum"].append(pool)
                 
        return results

    def get_best_opportunities(self, min_tvl: float = 1_000_000) -> List[Dict]:
        """
        Mencari opportunity terbaik di tiap chain dan membandingkannya.
        """
        scanned_data = self.scan_all_chains()
        opportunities = []

        for chain_key, pools in scanned_data.items():
            if not pools:
                continue
            
            # Cari pool dengan APY tertinggi yang lolos filter TVL
            safe_pools = [p for p in pools if p.tvl_usd >= min_tvl]
            if not safe_pools:
                continue
                
            best_pool = max(safe_pools, key=lambda x: x.apy)
            
            opportunities.append({
                "chain": chain_key,
                "chain_name": self.chains[chain_key]["name"],
                "project": best_pool.project,
                "pool": best_pool.pool,
                "apy": best_pool.apy,
                "tvl": best_pool.tvl_usd,
                "underlying": best_pool.underlying_tokens
            })

        # Sort berdasarkan APY tertinggi secara global
        return sorted(opportunities, key=lambda x: x["apy"], reverse=True)

    def migration_advice(self, current_chain: str, target_opportunity: Dict, capital: float) -> Dict:
        """
        Logika Predatror: Apakah layak pindah chain dengan modal tertentu?
        """
        if current_chain == target_opportunity["chain"]:
            return {"action": "STAY", "reason": "Already on the best chain."}

        # Hitung selisih profit bulanan
        # (Sangat sederhana: selisih APY * modal / 12)
        current_apy = 0 # Harus dapet data dari pool sekarang, assume 0 for demo
        apy_diff = target_opportunity["apy"] - current_apy
        monthly_extra_profit = (capital * (apy_diff / 100)) / 12
        
        # Balik modal bridge (break-even months)
        if monthly_extra_profit <= 0:
            return {"action": "STAY", "reason": "Target APY is not higher."}
            
        months_to_breakeven = self.bridge_fee_estimate / monthly_extra_profit
        
        if months_to_breakeven > 3: # Jika butuh > 3 bulan cuma buat balik modal bridge
            return {
                "action": "STAY", 
                "reason": f"Bridge fee too high for capital ${capital}. Breakeven in {months_to_breakeven:.1f} months."
            }
        
        return {
            "action": "MIGRATE", 
            "reason": f"Breakeven in {months_to_breakeven:.1f} months. Moving to {target_opportunity['chain_name']} is profitable."
        }
