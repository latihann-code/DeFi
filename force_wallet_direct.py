import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
wallet = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS", "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"))
whale = Web3.to_checksum_address("0xcfA3Ef56d303AE4fAabA0592388F19d7C3399FB4")
usdc_address = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")

# Slot 9 adalah slot balance USDC di Base
def set_bal(addr, amount_usd):
    slot = 9
    index = w3.keccak(hexstr=addr[2:].zfill(64) + hex(slot)[2:].zfill(64))
    amount_hex = hex(int(amount_usd * 10**6)).zfill(64)
    w3.provider.make_request("anvil_setStorageAt", [usdc_address, index.hex(), amount_hex])

set_bal(wallet, 1000)
set_bal(whale, 1000000)

abi = [{"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
c = w3.eth.contract(address=usdc_address, abi=abi)
print(f"Wallet: {c.functions.balanceOf(wallet).call()/1e6} USDC")
print(f"Whale: {c.functions.balanceOf(whale).call()/1e6} USDC")
