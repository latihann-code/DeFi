from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

usdc = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
vault = Web3.to_checksum_address("0x3D9E3b74Cb538D1996D2Bf871888d835284849fA")
burn_address = Web3.to_checksum_address("0x000000000000000000000000000000000000dEaD")

haram_amount_usd = 267.0218
haram_amount_wei = int(haram_amount_usd * 10**6)

abi = [
    {"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
    {"constant": False, "inputs": [{"name": "to", "type": "address"}, {"name": "value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"}
]
c = w3.eth.contract(address=usdc, abi=abi)

print(f"💼 Vault Balance Sebelum: ${c.functions.balanceOf(vault).call() / 1e6}")

# Impersonate Vault buat narik duitnya keluar
w3.provider.make_request("anvil_setBalance", [vault, hex(w3.to_wei(1, "ether"))])
w3.provider.make_request("anvil_impersonateAccount", [vault])

print(f"🔥 Membakar duit haram sebesar ${haram_amount_usd}...")
c.functions.transfer(burn_address, haram_amount_wei).transact({'from': vault})

w3.provider.make_request("anvil_stopImpersonatingAccount", [vault])

print(f"💼 Vault Balance Sesudah (HALAL): ${c.functions.balanceOf(vault).call() / 1e6}")
