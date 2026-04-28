from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
whale = Web3.to_checksum_address("0xcfA3Ef56d303AE4fAabA0592388F19d7C3399FB4")
usdc = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")

abi = [{"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
c = w3.eth.contract(address=usdc, abi=abi)

print(f"Initial Balance: {c.functions.balanceOf(whale).call()/1e6} USDC")

amount = hex(1000000 * 10**6).zfill(64)

for slot in range(100):
    # Mapping balance biasanya: keccak256(address + slot)
    index = w3.keccak(hexstr=whale[2:].zfill(64) + hex(slot)[2:].zfill(64))
    w3.provider.make_request("anvil_setStorageAt", [usdc, index.hex(), amount])
    
    new_bal = c.functions.balanceOf(whale).call()
    if new_bal > 100000 * 10**6:
        print(f"🔥 FOUND IT! Slot: {slot}")
        print(f"Current Balance: {new_bal/1e6} USDC")
        break

