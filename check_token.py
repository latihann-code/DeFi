from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
usdc = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
code = w3.eth.get_code(usdc)
print(f"Code Length: {len(code)}")
print(f"Code Start: {code[:20].hex()}")
