from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
addr = Web3.to_checksum_address("0xcfA3Ef56d303AE4fAabA0592388F19d7C3399FB4")
abi = [{"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"}]
c = w3.eth.contract(address=addr, abi=abi)
try:
    print(f"Contract Name: {c.functions.name().call()}")
except Exception as e:
    print(f"Probably an EOA or no name() function: {e}")
