import os
from web3 import Web3
from dotenv import load_dotenv
import json

load_dotenv()
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

wallet_address = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))
usdc_address = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")

# USDC Base Balance Slot is usually 0 or 1. We will try to find it or just set it.
# Actually, the easiest way is anvil_setBalance for ETH, 
# and for USDC we can use a known rich address and transfer.
# Let's use the Coinbase address on Base: 0x330E661f4356E87889A1201D86b3602f3C57973B (Wait, I used this)
# Let's try 0x476586D30867F213459e742B28B3698B3D3cc7Ca (Another rich one)

def setup():
    # 1. Reset ETH
    w3.provider.make_request("anvil_setBalance", [wallet_address, hex(w3.to_wei(10, "ether"))])
    
    # 2. Force USDC via anvil_setStorageAt
    # We will set balance for slot 0 (common for USDC)
    # But slot can vary. Let's use a simpler way: impersonate a REALLY rich one.
    # Coinbase: 0x330E661f4356E87889A1201D86b3602f3C57973B
    rich_address = Web3.to_checksum_address("0x330E661f4356E87889A1201D86b3602f3C57973B")
    
    # Give the rich address some ETH to pay for gas
    w3.provider.make_request("anvil_setBalance", [rich_address, hex(w3.to_wei(1, "ether"))])
    w3.provider.make_request("anvil_impersonateAccount", [rich_address])
    
    usdc_abi = [
        {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
        {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"}
    ]
    usdc_contract = w3.eth.contract(address=usdc_address, abi=usdc_abi)
    
    # Check rich balance first
    rich_bal = usdc_contract.functions.balanceOf(rich_address).call()
    print(f"Rich address balance: {rich_bal / 10**6} USDC")
    
    if rich_bal < 5 * 10**6:
        # If Coinbase is broke, try another one: Circle
        rich_address = Web3.to_checksum_address("0x476586D30867F213459e742B28B3698B3D3cc7Ca")
        w3.provider.make_request("anvil_setBalance", [rich_address, hex(w3.to_wei(1, "ether"))])
        w3.provider.make_request("anvil_impersonateAccount", [rich_address])
        print(f"Switched to Circle Whale: {rich_address}")

    tx_hash = usdc_contract.functions.transfer(wallet_address, 5 * 10**6).transact({'from': rich_address})
    w3.eth.wait_for_transaction_receipt(tx_hash)
    
    final_bal = usdc_contract.functions.balanceOf(wallet_address).call()
    print(f"✅ Final Balance for {wallet_address}: {final_bal / 10**6} USDC")

    with open("predator_state.json", "w") as f:
        json.dump({"capital": 5.0, "current_chain": "base", "last_update": "2026-04-24T00:00:00", "current_pool": None}, f)

if __name__ == "__main__":
    setup()
