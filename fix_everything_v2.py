from web3 import Web3
import os
import json
from dotenv import load_dotenv

load_dotenv()
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
usdc = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
# Alamat Pool WETH/USDC Aerodrome yang beneran SULTAN
real_sultan = Web3.to_checksum_address("0xd0b53D9277642d2a2b0a9697b0624470A59647e7")
whale_kita = Web3.to_checksum_address("0xcfA3Ef56d303AE4fAabA0592388F19d7C3399FB4")
wallet = Web3.to_checksum_address("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")

abi = [{"constant": False, "inputs": [{"name": "to", "type": "address"}, {"name": "value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
       {"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
c = w3.eth.contract(address=usdc, abi=abi)

def fix():
    # 1. Kasih modal ETH ke Sultan
    w3.provider.make_request("anvil_setBalance", [real_sultan, hex(w3.to_wei(10, "ether"))])
    w3.provider.make_request("anvil_impersonateAccount", [real_sultan])
    
    # 2. Transfer 1,000,000 USDC ke Whale kita (biar script bot gak perlu diubah alamatnya)
    # Tapi kita cek dulu saldo sultannya
    sultan_bal = c.functions.balanceOf(real_sultan).call()
    print(f"Sultan Balance: {sultan_bal/1e6} USDC")
    
    amount = 1000000 * 10**6
    c.functions.transfer(whale_kita, amount).transact({'from': real_sultan})
    
    # 3. Pastiin wallet lu juga punya $38.10
    c.functions.transfer(wallet, int(38.100515 * 10**6)).transact({'from': real_sultan})
    
    w3.provider.make_request("anvil_stopImpersonatingAccount", [real_sultan])
    print(f"✅ Fix Berhasil! Saldo Whale: {c.functions.balanceOf(whale_kita).call()/1e6} USDC")
    print(f"✅ Saldo Wallet: {c.functions.balanceOf(wallet).call()/1e6} USDC")

if __name__ == "__main__":
    fix()
