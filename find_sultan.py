from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
usdc = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")

# Daftar alamat yang biasanya "Sultan" USDC di Base
sultans = [
    "0x3300f17e6988C64348409409B1133c8711883585", # Circle / Coinbase
    "0xf89d7b9CB797c61106122839497d4937034d1c97", # Aerodrome Pool
    "0x1561Ad72496739B8180E1d86d5C849B497fD4B69", # Uniswap Pool
    "0x43063852079031c50e0513e9a409409B1133c871", # Aave
    "0x3D9E3b74Cb538D1996D2Bf871888d835284849fA", # Aerodrome Vault
    "0x6e9d7b9CB797c61106122839497d4937034d1c97"
]

abi = [{"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"},
       {"constant": False, "inputs": [{"name": "to", "type": "address"}, {"name": "value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"}]
c = w3.eth.contract(address=usdc, abi=abi)

for s in sultans:
    try:
        bal = c.functions.balanceOf(Web3.to_checksum_address(s)).call()
        if bal > 1000000 * 10**6:
            print(f"💎 SULTAN FOUND: {s} | Balance: {bal/1e6} USDC")
            # Langsung transfer ke Whale kita
            whale = Web3.to_checksum_address("0xcfA3Ef56d303AE4fAabA0592388F19d7C3399FB4")
            w3.provider.make_request("anvil_setBalance", [s, hex(w3.to_wei(1, "ether"))])
            w3.provider.make_request("anvil_impersonateAccount", [s])
            c.functions.transfer(whale, 1000000 * 10**6).transact({'from': s})
            print(f"✅ Transferred 1,000,000 USDC to Whale from {s}")
            break
    except: pass

