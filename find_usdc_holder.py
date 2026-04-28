import requests
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
usdc_address = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

# Holders USDC besar di Base (Coinbase, CEX, dsb)
holders = [
    "0x3300f17e6988C64348409409B1133c8711883585", # Circle
    "0x20ee038936ef670A88981f4a4603B6B711883585", # Coinbase
    "0xf89d7b9CB797c61106122839497d4937034d1c97", # Aerodrome Pool
    "0x1561Ad72496739B8180E1d86d5C849B497fD4B69", # Uniswap Pool
    "0x43063852079031c50e0513e9a409409B1133c871", # Aave Base
]

abi = [{"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
contract = w3.eth.contract(address=usdc_address, abi=abi)

for h in holders:
    try:
        bal = contract.functions.balanceOf(Web3.to_checksum_address(h)).call()
        print(f"Holder {h}: {bal / 1e6} USDC")
    except:
        pass
