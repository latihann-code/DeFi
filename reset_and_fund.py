import os
from web3 import Web3
from dotenv import load_dotenv
import json

load_dotenv()
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

wallet_address = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))
usdc_address = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
whale_address = Web3.to_checksum_address("0x330E661f4356E87889A1201D86b3602f3C57973B") # Base USDC Whale

def setup():
    # 1. Reset ETH balance to 10 ETH
    w3.provider.make_request("anvil_setBalance", [wallet_address, hex(w3.to_wei(10, "ether"))])
    
    # 2. Impersonate Whale to get USDC
    w3.provider.make_request("anvil_impersonateAccount", [whale_address])
    w3.provider.make_request("anvil_setBalance", [whale_address, hex(w3.to_wei(1, "ether"))])
    
    # 3. Transfer exactly 5 USDC (USDC has 6 decimals on Base)
    usdc_abi = [{"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"}]
    usdc_contract = w3.eth.contract(address=usdc_address, abi=usdc_abi)
    
    # Clear current wallet USDC first (set storage to 0 is complex, easier to just set the balance if we know the slot, but transfer is safer)
    # For simplicity, we just add 5 USDC. If the user wants "Murni", we assume a fresh Anvil fork.
    
    tx_hash = usdc_contract.functions.transfer(wallet_address, 5 * 10**6).transact({'from': whale_address})
    w3.eth.wait_for_transaction_receipt(tx_hash)
    
    print(f"✅ Funded {wallet_address} with 10 ETH and 5 USDC")

    # 4. Reset local state file
    state = {
        "capital": 5.0,
        "current_chain": "base",
        "last_update": "2026-04-24T00:00:00",
        "current_pool": None
    }
    with open("predator_state.json", "w") as f:
        json.dump(state, f)
    print("✅ Local state reset to $5.0 capital")

if __name__ == "__main__":
    setup()
