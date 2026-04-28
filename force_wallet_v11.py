from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
whale = Web3.to_checksum_address("0xcfA3Ef56d303AE4fAabA0592388F19d7C3399FB4")
usdc = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")

# Ambil Implementation address dari Proxy (slot 0x3608...)
impl_slot = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
impl = w3.eth.get_storage_at(usdc, impl_slot)
print(f"Implementation: {impl.hex()}")

# Brute force slot lagi tapi di Implementation
amount = hex(1000000 * 10**6).zfill(64)
for s in range(30):
    idx = w3.keccak(hexstr=whale[2:].zfill(64) + hex(s)[2:].zfill(64))
    w3.provider.make_request("anvil_setStorageAt", [usdc, idx.hex(), amount])

abi = [{"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
c = w3.eth.contract(address=usdc, abi=abi)
print(f"Whale USDC: {c.functions.balanceOf(whale).call()/1e6}")
