import os
from web3 import Web3
from dotenv import load_dotenv
import json

load_dotenv()
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

wallet = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS", "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"))
usdc = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
whale = Web3.to_checksum_address("0xcfA3Ef56d303AE4fAabA0592388F19d7C3399FB4")

def main():
    if not w3.is_connected():
        print("❌ Error: Anvil belum menyala.")
        return

    print(f"✅ Anvil terkoneksi. Funding wallet {wallet}...")
    
    # Load capital from state
    with open("predator_state.json", "r") as f:
        state = json.load(f)
        capital = state.get("capital", 38.100515)

    # Set ETH Balance for gas
    w3.provider.make_request("anvil_setBalance", [wallet, hex(w3.to_wei(10, "ether"))])
    
    # Impersonate whale to send USDC
    w3.provider.make_request("anvil_impersonateAccount", [whale])
    w3.provider.make_request("anvil_setBalance", [whale, hex(w3.to_wei(1, "ether"))])

    abi = [
        {"constant": False, "inputs": [{"name": "to", "type": "address"}, {"name": "value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
        {"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
    ]
    contract = w3.eth.contract(address=usdc, abi=abi)

    # Transfer the capital amount
    amount_units = int(capital * 10**6)
    tx = contract.functions.transfer(wallet, amount_units).transact({'from': whale})
    w3.eth.wait_for_transaction_receipt(tx)
    w3.provider.make_request("anvil_stopImpersonatingAccount", [whale])

    final_bal = contract.functions.balanceOf(wallet).call() / 1e6
    print(f"🎯 SALDO FINAL DOMPET: ${final_bal} USDC")
    print("✅ Wallet funded based on predator_state.json without resetting it.")

if __name__ == "__main__":
    main()
