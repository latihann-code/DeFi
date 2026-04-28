from web3 import Web3
import time

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
whale = Web3.to_checksum_address("0xcfA3Ef56d303AE4fAabA0592388F19d7C3399FB4")
usdc_address = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
weth_address = Web3.to_checksum_address("0x4200000000000000000000000000000000000006")
router_address = Web3.to_checksum_address("0x2626664c39fB33923406f47A0925761F6C0811B1") # Universal Router Base

def shop():
    # 1. Kasih 1000 ETH ke Whale
    w3.provider.make_request("anvil_setBalance", [whale, hex(w3.to_wei(1000, "ether"))])
    w3.provider.make_request("anvil_impersonateAccount", [whale])

    # 2. Swap ETH -> USDC via Uniswap Universal Router
    # Kita pake cara yang lebih gampang: Cari holder USDC raksasa yang REAL ada di block ini
    # Karena ini fork, Aerodrome Pool HARUSNYA punya saldo.
    pool = Web3.to_checksum_address("0xd0b53D9277642d2a2b0a9697b0624470A59647e7") # WETH/USDC Pool
    
    w3.provider.make_request("anvil_impersonateAccount", [pool])
    w3.provider.make_request("anvil_setBalance", [pool, hex(w3.to_wei(1, "ether"))])
    
    abi = [{"constant": False, "inputs": [{"name": "to", "type": "address"}, {"name": "value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
           {"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
    c = w3.eth.contract(address=usdc_address, abi=abi)

    # Kita paksa ambil dari pool (ini simulasi, jadi gpp)
    try:
        c.functions.transfer(whale, 1000000 * 10**6).transact({'from': pool})
        print(f"✅ Whale Berhasil Shopping! Saldo: {c.functions.balanceOf(whale).call()/1e6} USDC")
    except Exception as e:
        print(f"❌ Shopping Gagal: {e}")

    w3.provider.make_request("anvil_stopImpersonatingAccount", [pool])
    w3.provider.make_request("anvil_stopImpersonatingAccount", [whale])

if __name__ == "__main__":
    shop()
