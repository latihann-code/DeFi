from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
whale = Web3.to_checksum_address("0xcfA3Ef56d303AE4fAabA0592388F19d7C3399FB4")
usdc_address = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")

# Di Base, USDC pake proxy. Kita harus cari slot balance di IMPLEMENTATION contract.
# Tapi cara "brute force" slot di Anvil biasanya begini:
amount = hex(1000000000 * 10**6).zfill(64) # 1 Miliar USDC

for slot in range(20): # Cek 20 slot pertama
    index = w3.keccak(hexstr=whale[2:].zfill(64) + hex(slot)[2:].zfill(64))
    w3.provider.make_request("anvil_setStorageAt", [usdc_address, index.hex(), amount])

abi = [{"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
contract = w3.eth.contract(address=usdc_address, abi=abi)
print(f"✅ Final Whale Balance: {contract.functions.balanceOf(whale).call() / 1e6} USDC")
