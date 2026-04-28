from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
usdc = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
# Aerodrome Pool WETH/USDC - Pasti ada jutaan USDC
pool = Web3.to_checksum_address("0xd0b53D9277642d2a2b0a9697b0624470A59647e7")
abi = [{"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
c = w3.eth.contract(address=usdc, abi=abi)
print(f"Current Block: {w3.eth.block_number}")
print(f"Pool USDC: {c.functions.balanceOf(pool).call()/1e6}")
