from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
usdc = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
whale = Web3.to_checksum_address("0x70997970C51812dc3A010C7d01b50e0d17dc79C8")
wallet = Web3.to_checksum_address("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")
mimin = Web3.to_checksum_address("0x2230393EDAD0299b7E7B59F20AA856cD1bEd52e1")

w3.provider.make_request("anvil_setBalance", [mimin, hex(w3.to_wei(1, "ether"))])
w3.provider.make_request("anvil_impersonateAccount", [mimin])

# 1. configureMinter(mimin, 100 Milyar)
data_config = "0x4e44d956" + mimin[2:].zfill(64) + hex(100000000000 * 10**6)[2:].zfill(64)
w3.eth.send_transaction({"from": mimin, "to": usdc, "data": data_config})

# 2. mint(whale, 1 Milyar)
w3.eth.send_transaction({"from": mimin, "to": usdc, "data": "0x40c10f19" + whale[2:].zfill(64) + hex(1000000000 * 10**6)[2:].zfill(64)})

# 3. mint(wallet, $267.0218)
w3.eth.send_transaction({"from": mimin, "to": usdc, "data": "0x40c10f19" + wallet[2:].zfill(64) + hex(int(267.0218 * 10**6))[2:].zfill(64)})

abi_bal = [{"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
c_bal = w3.eth.contract(address=usdc, abi=abi_bal)
print(f"💰 WHALE READY: {c_bal.functions.balanceOf(whale).call()/1e6} USDC")
print(f"💰 WALLET READY: {c_bal.functions.balanceOf(wallet).call()/1e6} USDC")

