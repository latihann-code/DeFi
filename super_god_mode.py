from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
usdc = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
# Kita bikin dompet biasa (EOA) buat jadi Whale baru
new_whale = Web3.to_checksum_address("0x70997970C51812dc3A010C7d01b50e0d17dc79C8") # Anvil Account #1
wallet = Web3.to_checksum_address("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266") # Anvil Account #0

def force_usdc(target_addr, amount_usd):
    amount_hex = hex(int(amount_usd * 10**6)).zfill(64)
    abi = [{"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
    c = w3.eth.contract(address=usdc, abi=abi)
    
    # Brute force slot 0-20 untuk EOA (biasanya slot 0 atau 9)
    for slot in range(20):
        index = w3.keccak(hexstr=target_addr[2:].zfill(64) + hex(slot)[2:].zfill(64))
        w3.provider.make_request("anvil_setStorageAt", [usdc, index.hex(), amount_hex])
        if c.functions.balanceOf(target_addr).call() == int(amount_usd * 10**6):
            print(f"✅ Slot {slot} works for {target_addr}")
            return True
    return False

print("🚀 Forcing USDC balances into EOAs...")
force_usdc(new_whale, 1000000)
force_usdc(wallet, 38.100515)

# 2. Modif the_pilot_loop.py biar pake Whale baru
with open("the_pilot_loop.py", "r") as f:
    code = f.read()

# Ganti alamat whale lama ke yang baru
new_code = code.replace("0xcfA3Ef56d303AE4fAabA0592388F19d7C3399FB4", "0x70997970C51812dc3A010C7d01b50e0d17dc79C8")

with open("the_pilot_loop.py", "w") as f:
    f.write(new_code)

print("✅ the_pilot_loop.py updated to use NEW Whale.")
