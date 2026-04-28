import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

whale = Web3.to_checksum_address("0xcfA3Ef56d303AE4fAabA0592388F19d7C3399FB4")
usdc_address = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")

# Slot saldo USDC di contract (Base USDC biasanya slot 0 atau 9, tapi kita pake metode transfer aja dari Rich Account)
# Cara paling aman di Anvil: Ambil dari Account yang punya USDC banyak di Base
rich_usdc_holder = Web3.to_checksum_address("0x3300f17e6988C64348409409B1133c8711883585") # Circle: USDC Bundler

def refill():
    if not w3.is_connected():
        print("Anvil not connected")
        return

    # 1. Kasih ETH buat gas ke Rich Holder
    w3.provider.make_request("anvil_setBalance", [rich_usdc_holder, hex(w3.to_wei(1, "ether"))])
    
    # 2. Impersonate Rich Holder
    w3.provider.make_request("anvil_impersonateAccount", [rich_usdc_holder])
    
    abi = [{"constant": False, "inputs": [{"name": "to", "type": "address"}, {"name": "value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"}]
    contract = w3.eth.contract(address=usdc_address, abi=abi)
    
    # 3. Kirim 1,000,000 USDC ke Whale kita
    amount = 1000000 * 10**6
    tx = contract.functions.transfer(whale, amount).transact({'from': rich_usdc_holder})
    w3.eth.wait_for_transaction_receipt(tx)
    
    w3.provider.make_request("anvil_stopImpersonatingAccount", [rich_usdc_holder])
    print(f"✅ Whale Refilled! Saldo Whale sekarang: {contract.functions.balanceOf(whale).call() / 1e6} USDC")

if __name__ == "__main__":
    refill()
