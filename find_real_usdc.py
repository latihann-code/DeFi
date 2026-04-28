from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
usdc = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")

# Daftar Pool Aerodrome / Uniswap yang harusnya punya jutaan USDC
targets = [
    "0xcfA3Ef56d303AE4fAabA0592388F19d7C3399FB4", # Aerodrome WETH/USDC
    "0x4200000000000000000000000000000000000006", # WETH (cuma buat tes)
    "0x3300f17e6988C64348409409B1133c8711883585"  # Circle
]

abi = [{"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
c = w3.eth.contract(address=usdc, abi=abi)

for t in targets:
    t_addr = Web3.to_checksum_address(t)
    try:
        bal = c.functions.balanceOf(t_addr).call()
        print(f"Address {t}: {bal/1e6} USDC")
    except Exception as e:
        print(f"Error {t}: {e}")

