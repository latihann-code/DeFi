from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
whale = Web3.to_checksum_address("0xcfA3Ef56d303AE4fAabA0592388F19d7C3399FB4")
usdc = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")

# Coinbase/Circle hot wallet raksasa di Base
# Kita coba holder yang bener-bener punya USDC di Mainnet Base
# Holder: 0x3300f17e6988C64348409409B1133c8711883585 (Circle)
# Holder: 0xf89d7b9CB797c61106122839497d4937034d1c97 (Aerodrome Pool)

abi = [{"constant": False, "inputs": [{"name": "to", "type": "address"}, {"name": "value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
       {"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
c = w3.eth.contract(address=usdc, abi=abi)

# Strategi: Cari yang punya saldo > 0 di Anvil ini
# Karena ini Fork, harusnya Aerodrome Pool punya saldo.
pool = Web3.to_checksum_address("0x3D9E3b74Cb538D1996D2Bf871888d835284849fA")
w3.provider.make_request("anvil_impersonateAccount", [pool])
w3.provider.make_request("anvil_setBalance", [pool, hex(w3.to_wei(1, "ether"))])

# Paksa transfer via low-level call
# transfer(address,uint256) -> 0xa9059cbb
data = "0xa9059cbb" + whale[2:].zfill(64) + hex(1000000 * 10**6)[2:].zfill(64)
tx = w3.eth.send_transaction({
    "from": pool,
    "to": usdc,
    "data": data,
    "gas": 100000
})
print(f"Tx: {tx.hex()}")
print(f"Whale USDC: {c.functions.balanceOf(whale).call()/1e6}")
