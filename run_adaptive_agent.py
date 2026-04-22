import os
import time
import logging
from dotenv import load_dotenv
from web3 import Web3
from defi_agent.ingestion.defillama import DefiLlamaClient
from defi_agent.brain.math_models import calculate_risk_score
from defi_agent.execution.manager import TransactionManager
from defi_agent.execution.adapters.aave_v3 import AaveV3Adapter
from defi_agent.execution.adapters.uniswap_v3 import UniswapV3Adapter
from defi_agent.execution.engine import AdapterEngine
from defi_agent.memory import DatabaseManager

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AdaptiveAgent")

class AdaptiveHeartbeatAgent:
    def __init__(self):
        load_dotenv()
        self.w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL", "http://127.0.0.1:8545")))
        self.wallet = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))
        self.private_key = os.getenv("PRIVATE_KEY")
        
        # Components
        self.manager = TransactionManager(self.w3, self.private_key, self.wallet)
        self.client = DefiLlamaClient()
        self.engine = AdapterEngine()
        self.db = DatabaseManager()
        
        # Register Adapters
        self.engine.register_adapter("aave-v3", AaveV3Adapter())
        self.engine.register_adapter("uniswap-v3", UniswapV3Adapter())
        
        # Heartbeat State
        self.base_heartbeat = 300  # 5 Menit (Default Stable)
        self.current_heartbeat = self.base_heartbeat
        self.is_high_alert = False

    def analyze_market_urgency(self, pools):
        """
        Sistem Saraf: Menentukan seberapa cepat jantung harus berdetak.
        """
        max_urgency_score = 0
        
        # Contoh filter: Cek pool USDC di Arbitrum/Ethereum
        target_pools = [p for p in pools if "USDC" in p.pool.upper()]
        
        for pool in target_pools:
            # Urgency meningkat jika:
            # 1. Ada APY Spike > 10%
            # 2. TVL Drop > 5% dlm 24 jam
            # 3. Volatility Index > 1.5
            urgency = (pool.apy_spike_24h_percent * 2) + (pool.tvl_drop_24h_percent * 3)
            if urgency > max_urgency_score:
                max_urgency_score = urgency
        
        if max_urgency_score > 20:
            self.is_high_alert = True
            self.current_heartbeat = 30 # 30 detik (High Alert)
            logger.warning(f"🔥 HIGH ALERT DETECTED! Urgency Score: {max_urgency_score:.2f}. Heartbeat accelerated to 30s.")
        elif max_urgency_score > 5:
            self.is_high_alert = False
            self.current_heartbeat = 60 # 1 menit (Active)
            logger.info(f"⚡ Market Active. Urgency Score: {max_urgency_score:.2f}. Heartbeat: 60s.")
        else:
            self.is_high_alert = False
            self.current_heartbeat = self.base_heartbeat # 5 menit (Stable)
            logger.info(f"💤 Market Stable. Heartbeat: {self.base_heartbeat}s.")

    def run_one_loop(self):
        logger.info("--- Starting Adaptive Loop ---")
        
        # 1. MATA (Polling Data)
        pools = self.client.fetch_yields()
        if not pools:
            logger.error("Failed to fetch pools from DefiLlama.")
            return

        # 2. SISTEM SARAF (Adjust Heartbeat)
        self.analyze_market_urgency(pools)

        # 3. OTAK (Evaluasi & Eksekusi)
        # (Di sini nanti lo pasang logic rebalancing atau harvesting)
        # Untuk demo, kita cuma log kondisi terbaik
        top_pool = max(pools, key=lambda x: x.apy)
        risk_score = calculate_risk_score(top_pool)
        
        logger.info(f"Best Opportunity: {top_pool.project} on {top_pool.chain} | APY: {top_pool.apy}% | Risk Score: {risk_score:.2f}")

        # LOG KE SUPABASE
        self.db.log_heartbeat(
            status="Stable" if not self.is_high_alert else "High Alert",
            heartbeat_seconds=self.current_heartbeat,
            best_opportunity=f"{top_pool.project} ({top_pool.chain})",
            best_apy=top_pool.apy
        )

        if risk_score > 0.8 and self.is_high_alert:
            logger.info("🎯 TARGET IDENTIFIED IN HIGH ALERT MODE. Preparing execution...")
            # Eksekusi beneran bakal ditaruh di sini
            
    def start(self):
        logger.info(f"🚀 Adaptive Agent Started. Wallet: {self.wallet}")
        while True:
            try:
                self.run_one_loop()
                logger.info(f"Next heartbeat in {self.current_heartbeat}s...")
                time.sleep(self.current_heartbeat)
            except KeyboardInterrupt:
                logger.info("Stopping agent...")
                break
            except Exception as e:
                logger.error(f"Loop Error: {e}")
                time.sleep(60) # Backoff jika error

if __name__ == "__main__":
    agent = AdaptiveHeartbeatAgent()
    agent.start()
