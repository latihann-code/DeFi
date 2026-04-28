from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
usdc = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
whale = Web3.to_checksum_address("0xcfA3Ef56d303AE4fAabA0592388F19d7C3399FB4")
# Coinbase hot wallet di Base
coinbase = Web3.to_checksum_address("0x3300f17e6988C64348409409B1133c8711883585")

w3.provider.make_request("anvil_setBalance", [coinbase, hex(w3.to_wei(10, "ether"))])
w3.provider.make_request("anvil_impersonateAccount", [coinbase])

# Pake bytecode inject buat force transfer
w3.provider.make_request("anvil_setBalance", [whale, hex(w3.to_wei(1, "ether"))])
print(f"Coinbase ETH: {w3.eth.get_balance(coinbase)}")
