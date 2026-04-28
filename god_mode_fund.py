from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
usdc = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
whale = Web3.to_checksum_address("0xcfA3Ef56d303AE4fAabA0592388F19d7C3399FB4")
wallet = Web3.to_checksum_address("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")

def find_and_set(target_addr, amount_usd):
    amount_hex = hex(int(amount_usd * 10**6)).zfill(64)
    # Brute force slot 0-100 dengan verifikasi langsung
    abi = [{"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
    c = w3.eth.contract(address=usdc, abi=abi)
    
    for slot in range(100):
        index = w3.keccak(hexstr=target_addr[2:].zfill(64) + hex(slot)[2:].zfill(64))
        w3.provider.make_request("anvil_setStorageAt", [usdc, index.hex(), amount_hex])
        if c.functions.balanceOf(target_addr).call() == int(amount_usd * 10**6):
            print(f"✅ Slot found for {target_addr}: {slot}")
            return True
    return False

print("🛠️  Setting God Mode Balances...")
find_and_set(whale, 1000000)
find_and_set(wallet, 38.100515)

abi = [{"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
c = w3.eth.contract(address=usdc, abi=abi)
print(f"💰 Final Wallet: {c.functions.balanceOf(wallet).call()/1e6} USDC")
print(f"💰 Final Whale: {c.functions.balanceOf(whale).call()/1e6} USDC")
