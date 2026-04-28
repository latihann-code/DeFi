import os
from web3 import Web3
from dotenv import load_dotenv
import json

load_dotenv()
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

wallet = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS", "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"))
usdc = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")

# Gunakan Pool Liquidity Aerodrome (WETH/USDC) yang saldonya jutaan dollar
whale = Web3.to_checksum_address("0xcfA3Ef56d303AE4fAabA0592388F19d7C3399FB4")

def main():
    if not w3.is_connected():
        print("❌ Error: Anvil belum menyala.")
        return

    print("✅ Anvil terkoneksi. Setup saldo...")
    
    # Set ETH Balance
    w3.provider.make_request("anvil_setBalance", [whale, hex(w3.to_wei(1, "ether"))])
    w3.provider.make_request("anvil_setBalance", [wallet, hex(w3.to_wei(10, "ether"))])
    
    w3.provider.make_request("anvil_impersonateAccount", [whale])

    abi = [
        {"constant": False, "inputs": [{"name": "to", "type": "address"}, {"name": "value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
        {"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
    ]
    contract = w3.eth.contract(address=usdc, abi=abi)

    whale_bal = contract.functions.balanceOf(whale).call()
    print(f"💰 Saldo Whale Aerodrome: {whale_bal / 1e6} USDC")

    # Kuras dulu saldo wallet supaya beneran murni $5
    bal = contract.functions.balanceOf(wallet).call()
    if bal > 0:
        w3.provider.make_request("anvil_impersonateAccount", [wallet])
        contract.functions.transfer(whale, bal).transact({'from': wallet})
        w3.provider.make_request("anvil_stopImpersonatingAccount", [wallet])

    # Transfer $5 Murni
    tx = contract.functions.transfer(wallet, 5 * 10**6).transact({'from': whale})
    w3.eth.wait_for_transaction_receipt(tx)
    w3.provider.make_request("anvil_stopImpersonatingAccount", [whale])

    final_bal = contract.functions.balanceOf(wallet).call() / 1e6
    print(f"🎯 SALDO FINAL DOMPET: ${final_bal} USDC")

    # Reset State Agent
    with open("predator_state.json", "w") as f:
        json.dump({"capital": 5.0, "current_chain": "base", "last_update": "2026-04-24T00:00:00", "current_pool": None}, f)
    print("✅ State Agent direset ke Capital $5.00")

if __name__ == "__main__":
    main()
