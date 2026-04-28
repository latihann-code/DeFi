from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
vitalik = Web3.to_checksum_address("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")
print(f"Vitalik ETH Balance on Base Fork: {w3.eth.get_balance(vitalik) / 1e18} ETH")
