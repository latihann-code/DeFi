import os
from dotenv import load_dotenv
from web3 import Web3
from defi_agent.execution.manager import TransactionManager

def main():
    load_dotenv()
    print("🤝 STARTING THE FINAL HANDSHAKE (ETH TRANSFER TEST)")
    
    # 1. Setup Connection
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    if not w3.is_connected():
        print("❌ Gagal konek ke Anvil! Pastikan 'anvil --fork-url' jalan.")
        return

    private_key = os.getenv("PRIVATE_KEY")
    wallet_address = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))
    manager = TransactionManager(w3, private_key, wallet_address)
    
    # 2. FUNDING ETH (The Anvil Magic)
    print(f"🛠️  Suntik 10 ETH ke {wallet_address}...")
    w3.provider.make_request("anvil_setBalance", [wallet_address, hex(w3.to_wei(10, "ether"))])
    
    initial_balance = w3.eth.get_balance(wallet_address)
    print(f"💰 Saldo Awal: {w3.from_wei(initial_balance, 'ether')} ETH")

    # 3. EXECUTION: Kirim 1 ETH ke Alamat Random
    random_receiver = Web3.to_checksum_address("0x000000000000000000000000000000000000dEaD")
    print(f"💸 Mengirim 1 ETH ke {random_receiver}...")
    
    tx = {
        "to": random_receiver,
        "value": w3.to_wei(1, "ether"),
        "gas": 21000 # Standard ETH Transfer gas
    }
    
    try:
        tx_hash = manager.send_transaction(tx)
        print(f"🎉 Transaksi Terkirim! Hash: {tx_hash}")
        
        print("⏳ Menunggu konfirmasi Anvil...")
        receipt = manager.wait_for_receipt(tx_hash)
        
        if receipt.status == 1:
            new_balance = w3.eth.get_balance(wallet_address)
            print("\n💎💎💎 MISSION ACCOMPLISHED! 💎💎💎")
            print(f"Saldo Akhir: {w3.from_wei(new_balance, 'ether')} ETH")
            print("Kesimpulan: Sistem Saraf & Tangan Bot lo 100% SEHAT!")
        else:
            print("❌ Transaksi Gagal di Blockchain.")
            
    except Exception as e:
        print(f"❌ Error saat eksekusi: {e}")

if __name__ == "__main__":
    main()
