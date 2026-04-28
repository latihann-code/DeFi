from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
usdc = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
vault = Web3.to_checksum_address("0x3D9E3b74Cb538D1996D2Bf871888d835284849fA")
abi = [{"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
c = w3.eth.contract(address=usdc, abi=abi)
print(f"Vault USDC Balance: {c.functions.balanceOf(vault).call()/1e6}")
