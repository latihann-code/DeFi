from web3 import Web3
from web3.types import TxParams
import time

class TransactionManager:
    def __init__(self, w3: Web3, private_key: str, wallet_address: str):
        self.w3 = w3
        self.private_key = private_key
        self.address = Web3.to_checksum_address(wallet_address)
        self.nonce = self.w3.eth.get_transaction_count(self.address)

    def get_gas_strategy(self, priority: str = "normal") -> dict:
        """
        Mengambil estimasi gas EIP-1559 (baseFee + priorityFee).
        """
        latest_block = self.w3.eth.get_block("latest")
        base_fee = latest_block.get("baseFeePerGas", self.w3.to_wei(20, "gwei"))
        
        # Priority Fee (Tip untuk miner/validator)
        if priority == "high":
            priority_fee = self.w3.to_wei(3, "gwei")
        else:
            priority_fee = self.w3.to_wei(1.5, "gwei")
            
        return {
            "maxFeePerGas": base_fee * 2 + priority_fee, # Buffer agar tidak stuck
            "maxPriorityFeePerGas": priority_fee
        }

    def refresh_nonce(self):
        self.nonce = self.w3.eth.get_transaction_count(self.address)

    def simulate_transaction(self, tx: dict):
        """Simulate a transaction using eth_call to catch reverts before spending gas."""
        try:
            self.w3.eth.call(tx)
        except Exception as e:
            raise RuntimeError(f"Pre-flight simulation failed: {str(e)}")

    def send_transaction(self, tx: dict, priority: str = "normal") -> str:
        """
        Melengkapi, menandatangani, dan mengirim transaksi.
        """
        # Lengkapi parameter dasar
        tx["from"] = self.address
        tx["nonce"] = self.nonce
        tx["chainId"] = self.w3.eth.chain_id
        
        # Pre-flight simulation
        self.simulate_transaction(tx)
        
        # Lengkapi Gas EIP-1559 jika belum ada
        if "maxFeePerGas" not in tx:
            gas_params = self.get_gas_strategy(priority)
            tx.update(gas_params)
        
        # Estimasi Gas Limit jika belum ada
        if "gas" not in tx:
            tx["gas"] = self.w3.eth.estimate_gas(tx)
            
        # Sign transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        
        # Send
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Increment nonce untuk transaksi berikutnya dalam loop yang sama
        self.nonce += 1
        
        return tx_hash.hex()

    def wait_for_receipt(self, tx_hash: str, timeout: int = 120) -> dict:
        """
        Menunggu konfirmasi transaksi.
        """
        return self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
