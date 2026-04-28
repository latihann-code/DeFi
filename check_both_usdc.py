from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

usdc_native = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
usdc_bridged = Web3.to_checksum_address("0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA")

# Alamat Pool Aerodrome WETH/USDC
pool = Web3.to_checksum_address("0xd0b53D9277642d2a2b0a9697b0624470A59647e7")

abi = [{"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]

def check(addr, name):
    c = w3.eth.contract(address=addr, abi=abi)
    try:
        bal = c.functions.balanceOf(pool).call()
        print(f"{name} Balance in Pool: {bal/1e6}")
    except:
        print(f"Error checking {name}")

check(usdc_native, "Native USDC")
check(usdc_bridged, "Bridged USDC (USDC.e)")
