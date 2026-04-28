from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
usdc = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
whale = Web3.to_checksum_address("0xcfA3Ef56d303AE4fAabA0592388F19d7C3399FB4")
pool = Web3.to_checksum_address("0x3D9E3b74Cb538D1996D2Bf871888d835284849fA")

w3.provider.make_request("anvil_setBalance", [pool, hex(w3.to_wei(1, "ether"))])
w3.provider.make_request("anvil_impersonateAccount", [pool])

abi = [{"constant": False, "inputs": [{"name": "to", "type": "address"}, {"name": "value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
       {"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
c = w3.eth.contract(address=usdc, abi=abi)

try:
    tx = c.functions.transfer(whale, 50000 * 10**6).transact({'from': pool})
    print(f"Success! Saldo Whale: {c.functions.balanceOf(whale).call()/1e6}")
except Exception as e:
    print(f"Failed: {e}")

w3.provider.make_request("anvil_stopImpersonatingAccount", [pool])
