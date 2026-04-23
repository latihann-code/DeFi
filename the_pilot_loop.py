import os
import time
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from defi_agent.ingestion.defillama import DefiLlamaClient
from defi_agent.ingestion.scanner import MultiChainScanner
from defi_agent.memory import DatabaseManager
from defi_agent.brain.filters import passes_safety_belts
from defi_agent.brain.math_models import calculate_expected_value
from defi_agent.ingestion.arbitrage import ArbitrageObserver
from defi_agent.ingestion.sniper import LiquidationObserver
from defi_agent.brain.looper import YieldLooperSimulator
from defi_agent.ingestion.alpha_scanner import AlphaDiscoveryScanner

# Setup Logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("week_marathon.log"), logging.StreamHandler()]
)
logger = logging.getLogger("DeFiWizardAgent")

class SevenDayPredator:
    def __init__(self, state_file="predator_state.json"):
        load_dotenv()
        self.client = DefiLlamaClient()
        self.scanner = MultiChainScanner()
        self.db = DatabaseManager()
        self.state_file = state_file
        
        # Modules - INTEL
        self.observer = ArbitrageObserver()
        self.sniper = LiquidationObserver()
        self.looper = YieldLooperSimulator()
        self.alpha_discovery = AlphaDiscoveryScanner()
        
        # Load State or Default
        self.load_state()
        
        self.current_pool = None 
        self.EV_HORIZON_DAYS = 7
        self.BRIDGE_COST = 1.5
        self.ANTI_CHURN_THRESHOLD = 1.05 # Lowered to be more aggressive
        self.SLEEP_STABLE = 60 # Dipercepat jadi 60 detik untuk demo
        self.last_summary_time = 0

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.capital = state.get("capital", 5.0)
                    self.current_chain = state.get("current_chain", "arbitrum")
                    logger.info(f"💾 State loaded: ${self.capital:.4f} on {self.current_chain}")
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
                self.capital = 5.0
                self.current_chain = "arbitrum"
        else:
            self.capital = 5.0
            self.current_chain = "arbitrum"

    def save_state(self):
        try:
            with open(self.state_file, 'w') as f:
                json.dump({
                    "capital": self.capital,
                    "current_chain": self.current_chain,
                    "last_update": datetime.now().isoformat()
                }, f)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def calculate_ev(self, pool, momentum_score=0.0):
        # We assume 100% of capital is deployed, no airdrop burn budget
        return calculate_expected_value(pool, self.capital, self.EV_HORIZON_DAYS, friction=0.01, momentum_score=momentum_score)

    def run_loop(self):
        logger.info(f"--- 🧙‍♂️ WIZARD MODE: YIELD STACKING & LOOPING (Chain: {self.current_chain} | Balance: ${self.capital:.4f}) ---")
        
        try:
            # 1. Narrative Tracking
            momentum_data = self.client.fetch_chain_momentum()
            hot_chains = [k for k, v in momentum_data.items() if v > 5]
            if hot_chains:
                logger.info(f"🔥 NARRATIVE: Capitalizing on Hot Chains: {hot_chains[:3]}")

            # 2. Alpha Discovery (Hidden Gems - Logging Only)
            all_pools = self.client.fetch_yields()
            
            # 3. Yield Hunting (Whitelisted + Momentum-Aware + Point Stacking)
            all_safe_pools = []
            for p in all_pools:
                # We relax TVL requirements slightly for CLMMs (Uniswap v3, Slipstream) to capture high fees
                if passes_safety_belts(p) or (p.tvl_usd > 200_000 and any(keyword in p.project.lower() for keyword in ["uniswap", "aerodrome", "pancakeswap", "orca"])):
                    # Fake 'has_points' if it's on a hot chain to boost EV for the triple play
                    if p.chain.lower() in hot_chains:
                        p.has_points = True
                    all_safe_pools.append(p)
            
            if not all_safe_pools:
                logger.warning("⚠️ No safe yields found. Holding cash.")
                self.current_pool = None
            else:
                # Rank with Momentum Score and EV
                ranked_pools = sorted(
                    all_safe_pools, 
                    key=lambda x: self.calculate_ev(x, momentum_score=momentum_data.get(x.chain.lower(), 0)), 
                    reverse=True
                )
                best_global = ranked_pools[0]
                best_global_ev = self.calculate_ev(best_global, momentum_score=momentum_data.get(best_global.chain.lower(), 0))

                if best_global_ev <= 0:
                    self.current_pool = None
                else:
                    local_pools = [p for p in ranked_pools if p.chain.lower() == self.current_chain]
                    best_local = local_pools[0] if local_pools else None
                    
                    decision = None
                    if not self.current_pool:
                        decision = best_local if best_local else best_global
                    else:
                        current_ev = self.calculate_ev(self.current_pool, momentum_score=momentum_data.get(self.current_chain, 0))
                        
                        # Compare Local Migration
                        if best_local and self.calculate_ev(best_local, momentum_score=momentum_data.get(self.current_chain, 0)) > (current_ev * self.ANTI_CHURN_THRESHOLD):
                            decision = best_local
                        
                        # Compare Global Migration
                        if best_global.chain.lower() != self.current_chain:
                            apy_local = (best_local.apy if best_local else self.current_pool.apy) / 100
                            apy_global = best_global.apy / 100
                            
                            # OG Logic: Loop leverage on Lending platforms
                            if "aave" in best_global.project.lower() or "morpho" in best_global.project.lower():
                                apy_global *= 2.5 # 2.5x Leverage Looping

                            extra_profit = self.capital * (apy_global - apy_local) * (7/365)
                            # If we can cover bridge costs in 7 days, we migrate
                            if extra_profit > self.BRIDGE_COST:
                                logger.info(f"🌉 MIGRATION APPROVED: Pindah ke {best_global.chain} buat {best_global.project}. Proyeksi extra profit 7D: ${extra_profit:.2f}")
                                self.capital -= self.BRIDGE_COST # Pay the bridge fee
                                decision = best_global

                    if decision:
                        self.current_pool = decision
                        self.current_chain = decision.chain.lower()

            if self.current_pool:
                effective_apy = self.current_pool.apy
                # Apply Looping leverage if lending protocol
                is_lending = any(l in self.current_pool.project.lower() for l in ["aave", "morpho", "radiant", "compound"])
                if is_lending:
                    effective_apy *= 2.5
                    logger.info(f"🔄 YIELD LOOPING ACTIVE: 2.5x Leverage on {self.current_pool.project}")
                
                # Apply CLMM Fee multiplier for tight ranges
                is_clmm = any(c in self.current_pool.project.lower() for c in ["uniswap-v3", "uniswap-v4", "aerodrome-slipstream", "orca", "cetus"])
                if is_clmm:
                    effective_apy *= 1.5 # Simulating tight tick range fees
                    logger.info(f"💧 CONCENTRATED LIQUIDITY: Tight Range LP on {self.current_pool.project}")

                # Simulasikan bunga 1 jam per detik untuk melihat growth-nya dengan cepat
                interest = self.capital * (effective_apy / 100) * (3600 / (365 * 24 * 3600))
                self.capital += interest
                logger.info(f"📈 Virtual Growth: +${interest:.8f} | Pool: {self.current_pool.project} ({self.current_pool.chain}) | Effective APY: {effective_apy:.2f}%")

            # --- DAILY BRIEFING ---
            current_time = time.time()
            if current_time - self.last_summary_time > 300: # Tiap 5 iterasi
                print("\n📊 --- DEFI WIZARD SUMMARY ---")
                print(f"🟢 [CORE] Capital: ${self.capital:.4f} | Chain: {self.current_chain.upper()}")
                print(f"💰 [ACTIVE] Pool: {self.current_pool.project if self.current_pool else 'CASH'} | APY: {self.current_pool.apy if self.current_pool else 0:.2f}%")
                if hot_chains:
                    print(f"🟡 [SCOUT] Hot Chains Tracking: {hot_chains[:3]}")
                print("-" * 45 + "\n")
                
                self.db.log_heartbeat(
                    status="WIZARD_MODE_STACKING",
                    heartbeat_seconds=self.SLEEP_STABLE,
                    best_opportunity=f"{self.current_pool.project if self.current_pool else 'CASH'}",
                    best_apy=self.current_pool.apy if self.current_pool else 0
                )
                self.last_summary_time = current_time

            self.save_state()
            return self.SLEEP_STABLE

        except Exception as e:
            logger.error(f"Predator Error: {e}")
            import traceback
            traceback.print_exc()
            return 60

    def start(self):
        logger.info(f"🧙‍♂️ DEFI WIZARD MODE (Max Yield, Looping, Meta-Stacking). Balance: ${self.capital}")
        while True:
            try:
                next_sleep = self.run_loop()
                time.sleep(next_sleep)
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    agent = SevenDayPredator()
    agent.start()
