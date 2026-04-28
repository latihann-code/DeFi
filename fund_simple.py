from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
usdc = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
whale = "0xcfA3Ef56d303AE4fAabA0592388F19d7C3399FB4"

# Set ETH dulu
w3.provider.make_request("anvil_setBalance", [whale, hex(w3.to_wei(10, "ether"))])

# Pake deal command (Foundry cheatcode) kalo disupport, tapi kita pake impersonate
# Cari sumber USDC: Aerodrome Pool (biasanya jutaan)
pool = "0x3D9E3b74Cb538D1996D2Bf871888d835284849fA" # Aerodrome Vault

w3.provider.make_request("anvil_setBalance", [pool, hex(w3.to_wei(1, "ether"))])
w3.provider.make_request("anvil_impersonateAccount", [pool])

abi = [{"constant": False, "inputs": [{"name": "to", "type": "address"}, {"name": "value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"}]
c = w3.eth.contract(address=usdc, abi=abi)

# Transfer 10,000 USDC ke Whale
try:
    tx = c.functions.transfer(whale, 10000 * 10**6).transact({'from': pool})
    print(f"Success! Tx: {tx.hex()}")
except Exception as e:
    print(f"Failed: {e}")

w3.provider.make_request("anvil_stopImpersonatingAccount", [pool])
