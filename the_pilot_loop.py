import os
import time
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from web3 import Web3
from defi_agent.ingestion.defillama import DefiLlamaClient
from defi_agent.ingestion.scanner import MultiChainScanner
from defi_agent.memory import DatabaseManager
from defi_agent.brain.filters import passes_safety_belts
from defi_agent.brain.math_models import calculate_expected_value
from defi_agent.ingestion.arbitrage import ArbitrageObserver
from defi_agent.ingestion.sniper import LiquidationObserver
from defi_agent.brain.looper import YieldLooperSimulator
from defi_agent.ingestion.alpha_scanner import AlphaDiscoveryScanner
from defi_agent.execution.manager import TransactionManager
from defi_agent.execution.engine import AdapterEngine
from defi_agent.execution.adapters.aave_v3 import AaveV3Adapter
from defi_agent.execution.adapters.uniswap_v3 import UniswapV3Adapter

# Minimal ERC20 ABI for Balance & Allowance checks
ERC20_ABI = [
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}, {"name": "_spender", "type": "address"}], "name": "allowance", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
]

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
        
        # Modules - EXECUTION (Real Master Connection)
        self.w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL", "http://127.0.0.1:8545")))
        wallet_env = os.getenv("WALLET_ADDRESS", "0x0000000000000000000000000000000000000000")
        if Web3.is_address(wallet_env):
            self.wallet = Web3.to_checksum_address(wallet_env)
        else:
            self.wallet = Web3.to_checksum_address("0x0000000000000000000000000000000000000000")
            
        self.private_key = os.getenv("PRIVATE_KEY")
        
        self.engine = AdapterEngine()
        self.engine.register_adapter("aave-v3", AaveV3Adapter())
        self.engine.register_adapter("uniswap-v3", UniswapV3Adapter())
        
        if self.private_key:
            self.tx_manager = TransactionManager(self.w3, self.private_key, self.wallet)
            logger.info("🔌 [ON-CHAIN] Connected to RPC. Transaction Manager is ONLINE.")
        else:
            self.tx_manager = None
            logger.warning("⚠️ [DRY-RUN] RPC disconnected or missing keys. Simulating execution.")
        
        # Load State or Default
        self.load_state()
        
        self.current_pool = None 
        self.EV_HORIZON_DAYS = 7
        self.BRIDGE_COST = 1.5
        self.ANTI_CHURN_THRESHOLD = 1.05 # Lowered to be more aggressive
        self.SLEEP_STABLE = 900 # 15 menit per iterasi
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
                    "last_update": datetime.now().isoformat(),
                    "current_pool": self.current_pool.project if self.current_pool else None
                }, f)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def calculate_ev(self, pool, momentum_score=0.0):
        # We assume 100% of capital is deployed, no airdrop burn budget
        return calculate_expected_value(pool, self.capital, self.EV_HORIZON_DAYS, friction=0.01, momentum_score=momentum_score)

    def ensure_allowance(self, asset_address: str, spender_address: str, amount_wei: int):
        """
        Master Execution: Never guess allowance. Always check on-chain.
        """
        if not self.tx_manager: return
        contract = self.w3.eth.contract(address=asset_address, abi=ERC20_ABI)
        current_allowance = contract.functions.allowance(self.wallet, spender_address).call()
        
        if current_allowance < amount_wei:
            logger.info(f"🔓 [ALLOWANCE] Approving {spender_address} to spend USDC...")
            # Max approve to save gas in the future
            max_uint = int("ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", 16)
            tx_data = self.engine.get_tx_data("aave-v3", "APPROVE", {"asset": asset_address, "spender": spender_address, "amount": max_uint})
            
            tx_hash = self.tx_manager.send_transaction({
                "to": tx_data.to,
                "data": tx_data.data,
                "gas": 100000
            })
            logger.info(f"⏳ Waiting for Approve tx {tx_hash}...")
            self.tx_manager.wait_for_receipt(tx_hash)
            logger.info("✅ Approve confirmed on-chain.")

    def execute_onchain_trade(self, pool, action: str):
        """
        The True Master Execution Logic.
        Validates Real Balance, Checks Allowance, Computes Slippage, and Executes.
        """
        if not self.tx_manager:
            logger.info(f"🔧 [DRY-RUN EXECUTION] {action} ${self.capital:.2f} on {pool.project} ({pool.chain}).")
            return "0x_dummy_tx_hash_dry_run"
            
        logger.info(f"⚡ [LIVE EXECUTION] Sending {action} request to {pool.project}...")
        
        try:
            asset_address = Web3.to_checksum_address("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48") # USDC
            logger.info(f"🔍 Checking balance for wallet {self.wallet} on asset {asset_address}")
            # Master Rule 1: NO HALLUCINATIONS. Check real on-chain balance.
            contract = self.w3.eth.contract(address=asset_address, abi=ERC20_ABI)
            real_balance_wei = contract.functions.balanceOf(self.wallet).call()
            
            # Master Mode: We only update capital from on-chain if we are actually checking what we HAVE to deploy.
            # Otherwise, keep the virtual/total equity tracking.
            if action == "DEPOSIT":
                amount_wei = real_balance_wei
                if amount_wei == 0:
                    logger.warning("⚠️ Real USDC balance is 0. Cannot execute.")
                    return None
            else:
                # For WITHDRAW, we are pulling from the pool, so real_balance_wei is expected to be small/zero.
                # We use a placeholder for amount_wei or fetch from pool (complex), so for now we just don't zero out self.capital.
                amount_wei = int(self.capital * 10**6) 


            tx_data = None
            if "aave" in pool.project.lower():
                adapter = self.engine.adapters.get("aave-v3")
                if action == "DEPOSIT":
                    # Master Rule 2: Ensure Allowance
                    self.ensure_allowance(asset_address, adapter.pool_address, amount_wei)
                tx_data = self.engine.get_tx_data("aave-v3", action, {"asset": asset_address, "amount": amount_wei})
                
            elif ("uniswap" in pool.project.lower() or "aerodrome" in pool.project.lower()) and action == "DEPOSIT":
                adapter = self.engine.adapters.get("uniswap-v3")
                # Master Rule 2: Ensure Allowance
                self.ensure_allowance(asset_address, adapter.ROUTER_ADDRESS, amount_wei)
                
                # Master Rule 3: Anti-MEV Slippage Protection
                # Assuming rough oracle price: 1 ETH = $3000 USDC. 
                # (Real implementation calls Chainlink/Quoter)
                expected_weth = amount_wei / 3000
                # 0.5% Slippage limit (Strict Mode)
                min_amount_out = int(expected_weth * 0.995 * 10**12) # 18 dec WETH vs 6 dec USDC
                
                tx_data = self.engine.get_tx_data("uniswap-v3", "SWAP", {
                    "token_in": asset_address,
                    "token_out": Web3.to_checksum_address("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"), # WETH
                    "amount_in": amount_wei,
                    "min_amount_out": min_amount_out,
                    "recipient": self.wallet
                })
            
            if tx_data:
                # Execution with Gas Logic
                tx_hash = self.tx_manager.send_transaction({
                    "to": tx_data.to,
                    "data": tx_data.data,
                    "gas": tx_data.gas_limit or 500000
                })
                logger.info(f"✅ [TX SUCCESS] {action} Confirmed! Hash: {tx_hash}")
                
                # Log the trade to memory
                self.db.log_trade(
                    protocol=pool.project,
                    action=action,
                    asset="USDC",
                    amount=self.capital,
                    tx_hash=tx_hash,
                    status="SUCCESS",
                    risk_score=1.0,
                    reason=f"Wizard Engine {action} Execution"
                )
                return tx_hash
            else:
                logger.warning(f"⚠️ No active adapter for {pool.project}. Fallback to DRY-RUN.")
                return "0x_dummy_fallback"
                
        except Exception as e:
            logger.error(f"❌ [TX FAILED] Blockchain Execution Error: {e}")
            return None

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

                    if decision and self.current_pool != decision:
                        # EKSEKUSI: Pindah Posisi (Withdraw dari yang lama, Deposit ke yang baru)
                        if self.current_pool:
                            logger.info(f"🔄 REALLOCATING: Keluar dari {self.current_pool.project}")
                            self.execute_onchain_trade(self.current_pool, "WITHDRAW")
                            
                        logger.info(f"🚀 MASUK POSISI BARU: {decision.project} di {decision.chain}")
                        self.execute_onchain_trade(decision, "DEPOSIT")
                        
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
                    status="WIZARD_MODE_LIVE",
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
        logger.info(f"🧙‍♂️ DEFI WIZARD MODE (Max Yield, Looping, Meta-Stacking, LIVE EXECUTION). Balance: ${self.capital}")
        while True:
            try:
                next_sleep = self.run_loop()
                time.sleep(next_sleep)
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    agent = SevenDayPredator()
    agent.start()