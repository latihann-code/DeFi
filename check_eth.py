from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
circle = Web3.to_checksum_address("0x3300f17e6988C64348409409B1133c8711883585")
print(f"Circle ETH Balance: {w3.eth.get_balance(circle) / 1e18} ETH")
