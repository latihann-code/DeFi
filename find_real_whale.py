from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
usdc = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
abi = [{"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
c = w3.eth.contract(address=usdc, abi=abi)

# Holders top dari mainnet Base (Circle, Binance, etc)
h = [
    "0x3300f17e6988C64348409409B1133c8711883585",
    "0x20ee038936ef670A88981f4a4603B6B711883585",
    "0x43063852079031c50e0513e9a409409B1133c871",
    "0xf89d7b9CB797c61106122839497d4937034d1c97"
]
for a in h:
    try:
        b = c.functions.balanceOf(w3.to_checksum_address(a)).call()
        print(f"{a}: {b/1e6}")
    except: pass
