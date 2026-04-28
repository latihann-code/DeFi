import json
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
whale = Web3.to_checksum_address("0xcfA3Ef56d303AE4fAabA0592388F19d7C3399FB4")
usdc_address = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")

# Set ETH
w3.provider.make_request("anvil_setBalance", [whale, hex(w3.to_wei(10, "ether"))])

# Brute force slot for Proxy/Implementation pattern
# USDC di Base pake Proxy, slot balance biasanya ada di slot 9
amount = hex(10000000 * 10**6).zfill(64)
for s in range(20):
    idx = w3.keccak(hexstr=whale[2:].zfill(64) + hex(s)[2:].zfill(64))
    w3.provider.make_request("anvil_setStorageAt", [usdc_address, idx.hex(), amount])

abi = [{"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
c = w3.eth.contract(address=usdc_address, abi=abi)
print(f"Whale USDC: {c.functions.balanceOf(whale).call() / 1e6}")
