import os
from dotenv import load_dotenv
from web3 import Web3
from defi_agent.models import PoolData
from defi_agent.brain.math_models import calculate_risk_score
from defi_agent.execution.manager import TransactionManager
from defi_agent.execution.adapters.aave_v3 import AaveV3Adapter

def main():
    load_dotenv()
    print("🚀 STARTING FINAL BOSS EXECUTION")
    
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    if not w3.is_connected():
        print("❌ Gagal konek ke Anvil!")
        return

    private_key = os.getenv("PRIVATE_KEY")
    wallet_address = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))
    manager = TransactionManager(w3, private_key, wallet_address)
    aave_adapter = AaveV3Adapter(wallet_address=wallet_address)
    
    # 1. Fund ETH
    w3.provider.make_request("anvil_setBalance", [wallet_address, hex(w3.to_wei(10, "ether"))])

    # 2. Fund USDC (HACKY WAY - Minta dari Whale yang PASTI punya)
    # USDC Whale: 0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640 (Binance)
    whale = Web3.to_checksum_address("0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640")
    usdc_address = Web3.to_checksum_address("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    
    print(f"🛠️ Borrowing USDC from Whale {whale}...")
    w3.provider.make_request("anvil_impersonateAccount", [whale])
    w3.provider.make_request("anvil_setBalance", [whale, hex(w3.to_wei(1, "ether"))])
    
    usdc_abi = [
        {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
        {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
        {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"}
    ]
    usdc_contract = w3.eth.contract(address=usdc_address, abi=usdc_abi)
    
    # Transfer 1000 USDC
    amount_transfer = 1000 * 10**6
    w3.eth.send_transaction({
        "from": whale,
        "to": usdc_address,
        "data": usdc_contract.encode_abi("transfer", [wallet_address, amount_transfer]),
        "gas": 100000
    })
    
    balance = usdc_contract.functions.balanceOf(wallet_address).call()
    print(f"✅ Wallet Balance: {balance / 10**6} USDC")

    if balance > 0:
        # 3. APPROVE
        print("🔑 Step 4A: Approving Aave...")
        aave_pool = Web3.to_checksum_address(aave_adapter.pool_address)
        approve_tx = manager.send_transaction({
            "to": usdc_address,
            "data": usdc_contract.encode_abi("approve", [aave_pool, balance])
        })
        manager.wait_for_receipt(approve_tx)
        
        # 4. SUPPLY
        print("💸 Step 4B: Supplying to Aave...")
        supply_amount = 100 * 10**6
        tx_data = aave_adapter.encode_deposit(usdc_address, supply_amount)
        tx_hash = manager.send_transaction({
            "to": tx_data.to,
            "data": tx_data.data,
            "gas": tx_data.gas_limit
        })
        
        receipt = manager.wait_for_receipt(tx_hash)
        if receipt.status == 1:
            print("\n💎💎💎 MISSION ACCOMPLISHED! 💎💎💎")
            print("Bot lo sukses eksekusi Aave V3 di Anvil Fork!")
        else:
            print("❌ Supply Failed.")
    else:
        print("❌ Masih 0 USDC bro, whale-nya pelit.")

if __name__ == "__main__":
    main()
