import os
import time
import logging
from dotenv import load_dotenv
from web3 import Web3
from defi_agent.ingestion.scanner import MultiChainScanner
from defi_agent.execution.manager import TransactionManager
from defi_agent.execution.adapters.aave_v3 import AaveV3Adapter
from defi_agent.memory import DatabaseManager

# Setup Logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("pilot_anvil.log"), logging.StreamHandler()]
)
logger = logging.getLogger("PilotAnvil")

class PilotAgentAnvil:
    def __init__(self):
        load_dotenv()
        self.scanner = MultiChainScanner()
        self.db = DatabaseManager()
        self.wallet = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))
        self.private_key = os.getenv("PRIVATE_KEY")
        
        # Simulasi Capital $5
        self.capital = 5.0 
        self.allowed_chains = ["base", "arbitrum"]
        
    def execute_deposit(self, chain_key: str, pool_data: dict):
        # Gunakan RPC Anvil lokal
        w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
        manager = TransactionManager(w3, self.private_key, self.wallet)
        adapter = AaveV3Adapter(chain=chain_key)
        
        # Alamat USDC Base (Simulasi)
        usdc_addr = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
        amount_wei = int(self.capital * 10**6)
        
        logger.info(f"🔥 [ANVIL] EXECUTING DEPOSIT: {self.capital} USDC to Aave V3 on {chain_key}")
        
        try:
            tx_data = adapter.encode_deposit(usdc_addr, amount_wei)
            
            # Patch wallet address ke dalam data (untuk demo)
            p_wallet = self.wallet[2:].lower().zfill(64)
            real_data = tx_data.data[:10+64+64] + p_wallet + tx_data.data[10+64+64+64:]
            
            # Kirim tanpa cek saldo (Anvil bakal nerima tapi mungkin revert di internal)
            tx_hash = manager.send_transaction({
                "to": tx_data.to,
                "data": real_data,
                "gas": tx_data.gas_limit
            })
            
            logger.info(f"✅ [ANVIL] TX SENT! Hash: {tx_hash}")
            self.db.log_trade(
                protocol="aave-v3", action="DEPOSIT", asset="USDC",
                amount=self.capital, tx_hash=tx_hash, status="SENT_ANVIL",
                risk_score=0.9, reason=f"Anvil Simulation on {chain_key}"
            )
            return tx_hash
        except Exception as e:
            logger.error(f"❌ [ANVIL] Failed: {e}")
            return None

    def run_loop(self):
        logger.info("📡 [ANVIL] Scanning for opportunities...")
        # Kita paksa ambil data real tapi eksekusi di lokal
        opportunities = self.scanner.get_best_opportunities(min_tvl=500_000)
        
        # Cari peluang di Base/Arb
        targets = [o for o in opportunities if o["chain"] in self.allowed_chains]
        
        if not targets:
            logger.info("💤 [ANVIL] No targets found. Waiting...")
            return

        best = targets[0]
        logger.info(f"🎯 [ANVIL] Target Found: {best['project']} on {best['chain_name']} | APY: {best['apy']}%")

        # EKSEKUSI TANPA CEK SALDO (Anvil Mode)
        self.execute_deposit(best["chain"], best)

    def start(self):
        logger.info("🦅 ANVIL PILOT LOOP STARTED (No Balance Check Mode)")
        while True:
            try:
                self.run_loop()
                logger.info("Sleeping for 60s before next heartbeat...")
                time.sleep(60) # Loop tiap 1 menit buat demo
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Loop Error: {e}")
                time.sleep(10)

if __name__ == "__main__":
    agent = PilotAgentAnvil()
    agent.start()
