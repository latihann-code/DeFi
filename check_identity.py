from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
addr = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
abi = [
    {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"}
]
c = w3.eth.contract(address=addr, abi=abi)
try:
    print(f"Name: {c.functions.name().call()}")
    print(f"Symbol: {c.functions.symbol().call()}")
    print(f"Decimals: {c.functions.decimals().call()}")
except Exception as e:
    print(f"Error: {e}")
