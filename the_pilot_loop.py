import os
import time
import json
import logging
import random
from datetime import datetime
from dotenv import load_dotenv
from web3 import Web3
from defi_agent.ingestion.defillama import DefiLlamaClient
from defi_agent.ingestion.scanner import MultiChainScanner
from defi_agent.memory import DatabaseManager
from defi_agent.brain.filters import passes_safety_belts
from defi_agent.brain.math_models import calculate_expected_value
from defi_agent.execution.airdrop import AirdropHunter
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
logger = logging.getLogger("PredatorAgent")

class SevenDayPredator:
    def __init__(self, state_file="predator_state.json"):
        load_dotenv()
        self.client = DefiLlamaClient()
        self.scanner = MultiChainScanner()
        self.db = DatabaseManager()
        self.state_file = state_file
        
        # Modules - EXECUTION
        self.airdrop = AirdropHunter(os.getenv("WALLET_ADDRESS", "0x0"))
        
        # Modules - INTEL (Read-Only)
        self.observer = ArbitrageObserver()
        self.sniper = LiquidationObserver()
        self.looper = YieldLooperSimulator()
        self.alpha_discovery = AlphaDiscoveryScanner()
        
        # Load State or Default
        self.load_state()
        
        self.current_pool = None 
        self.EV_HORIZON_DAYS = 7
        self.BRIDGE_COST = 1.5
        self.ANTI_CHURN_THRESHOLD = 1.15 
        self.SLEEP_STABLE = 900 
        self.AIRDROP_BUDGET = 1.0 
        self.last_summary_time = 0

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.capital = state.get("capital", 5.0)
                    self.current_chain = state.get("current_chain", "arbitrum")
                    self.airdrop.interaction_history = state.get("airdrop_history", {})
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
                    "airdrop_history": self.airdrop.interaction_history,
                    "last_update": datetime.now().isoformat()
                }, f)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def calculate_ev(self, pool, momentum_score=0.0):
        available_cap = self.capital - self.AIRDROP_BUDGET
        return calculate_expected_value(pool, available_cap, self.EV_HORIZON_DAYS, friction=0.01, momentum_score=momentum_score)

    def run_loop(self):
        logger.info(f"--- 📡 PREDATOR v3: SCAN & INTEL (Chain: {self.current_chain} | Balance: ${self.capital:.4f}) ---")
        
        try:
            # --- INTEL LAYER (Read-Only) ---
            # 1. Narrative Tracking (Hot Chains)
            momentum_data = self.client.fetch_chain_momentum()
            hot_chains = [k for k, v in momentum_data.items() if v > 5] # > 5% 7d growth
            logger.info(f"🔥 NARRATIVE: Hot Chains detected: {hot_chains[:3]}")

            # 2. Arbitrage Observer
            self.observer.scan_for_opportunities(self.capital)

            # 3. Liquidation Sniper (Mocked users)
            self.sniper.scan_liquidations()

            # 4. Yield Looping Simulation (Using current or best pool)
            if self.current_pool:
                self.looper.simulate_loop(self.current_pool.apy, borrow_apy=4.5)

            # --- EXECUTION LAYER ---
            # 5. Airdrop Hunter
            current_ts = time.time()
            airdrop_plan = self.airdrop.generate_footprint_plan(current_ts)
            for target in airdrop_plan:
                if self.airdrop.execute_simulated_footprint(target, amount=1.0):
                    self.airdrop.interaction_history[target["name"]] = current_ts
                    self.capital -= 0.05 

            # 6. Alpha Discovery (Hidden Gems - Logging Only)
            all_pools = self.client.fetch_yields()
            self.alpha_discovery.scan_for_alphas(all_pools)

            # 7. Yield Hunting (Whitelisted + Momentum-Aware)
            all_safe_pools = []
            for p in all_pools:
                if passes_safety_belts(p):
                    all_safe_pools.append(p)
            
            if not all_safe_pools:
                logger.warning("⚠️ No safe yields found. Holding cash.")
                self.current_pool = None
            else:
                # Rank with Momentum Score
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
                        if best_local and self.calculate_ev(best_local, momentum_score=momentum_data.get(self.current_chain, 0)) > (current_ev * self.ANTI_CHURN_THRESHOLD):
                            decision = best_local
                        
                        if best_global.chain.lower() != self.current_chain:
                            apy_local = (best_local.apy if best_local else self.current_pool.apy) / 100
                            apy_global = best_global.apy / 100
                            extra_profit = self.capital * (apy_global - apy_local) * (7/365)
                            if extra_profit > (self.BRIDGE_COST * 2):
                                decision = best_global

                    if decision:
                        self.current_pool = decision
                        self.current_chain = decision.chain.lower()

            if self.current_pool:
                interest = (self.capital - self.AIRDROP_BUDGET) * (self.current_pool.apy / 100) * (self.SLEEP_STABLE / (365 * 24 * 3600))
                self.capital += interest
                logger.info(f"📈 Virtual Growth: +${interest:.8f} | Pool: {self.current_pool.project} ({self.current_pool.chain})")

            # --- DAILY BRIEFING (Every hour for demo) ---
            current_time = time.time()
            if current_time - self.last_summary_time > 3600:
                print("\n📊 --- PREDATOR DAILY BRIEFING ---")
                print(f"💰 Capital: ${self.capital:.4f} | Chain: {self.current_chain}")
                print(f"🌾 Active Yield: {self.current_pool.project if self.current_pool else 'CASH'} ({self.current_pool.apy if self.current_pool else 0}%)")
                print(f"🔥 Hot Chains: {', '.join(hot_chains[:3])}")
                print(f"🪂 Airdrop Footprints: {len(self.airdrop.interaction_history)}")
                print("-" * 35 + "\n")
                
                self.db.log_heartbeat(
                    status="PREDATOR_V3_ACTIVE",
                    heartbeat_seconds=self.SLEEP_STABLE,
                    best_opportunity=f"{self.current_pool.project if self.current_pool else 'CASH'} ({self.current_chain})",
                    best_apy=self.current_pool.apy if self.current_pool else 0
                )
                self.last_summary_time = current_time

            self.save_state()
            return self.SLEEP_STABLE

        except Exception as e:
            logger.error(f"Predator Error: {e}")
            import traceback
            traceback.print_exc()
            return 300

    def start(self):
        logger.info(f"🦅 PREDATOR MODE v2.0 (Airdrop + Observer). Balance: ${self.capital}")
        while True:
            try:
                next_sleep = self.run_loop()
                time.sleep(next_sleep)
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    agent = SevenDayPredator()
    agent.start()
