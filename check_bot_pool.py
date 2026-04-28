from web3 import Web3
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
pool_name = 'aerodrome-slipstream'
pool_address = w3.to_checksum_address(w3.keccak(text=pool_name)[:20])
print(f'Pool Name: {pool_name}')
print(f'Bot Pool Address: {pool_address}')

usdc = Web3.to_checksum_address('0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913')
abi = [{'constant': True, 'inputs': [{'name': 'owner', 'type': 'address'}], 'name': 'balanceOf', 'outputs': [{'name': '', 'type': 'uint256'}], 'type': 'function'}]
c = w3.eth.contract(address=usdc, abi=abi)
print(f'USDC in Bot Pool: ${c.functions.balanceOf(pool_address).call()/1e6}')

wallet = Web3.to_checksum_address('0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266')
print(f'USDC in Wallet: ${c.functions.balanceOf(wallet).call()/1e6}')
