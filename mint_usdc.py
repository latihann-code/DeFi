from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
usdc = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
whale = Web3.to_checksum_address("0x70997970C51812dc3A010C7d01b50e0d17dc79C8")

# USDC Base (FiatTokenV2_1) punya fungsi masterMinter()
# Kita cari siapa tuannya
master_minter_abi = [{"constant": True, "inputs": [], "name": "masterMinter", "outputs": [{"name": "", "type": "address"}], "type": "function"}]
c_minter = w3.eth.contract(address=usdc, abi=master_minter_abi)

try:
    mimin = c_minter.functions.masterMinter().call()
    print(f"Mimin Found: {mimin}")
    
    # Kasih ETH ke Mimin
    w3.provider.make_request("anvil_setBalance", [mimin, hex(w3.to_wei(1, "ether"))])
    w3.provider.make_request("anvil_impersonateAccount", [mimin])
    
    # Mimin suruh cetak duit!
    # mint(address,uint256) -> 0x40c10f19
    data = "0x40c10f19" + whale[2:].zfill(64) + hex(1000000000 * 10**6)[2:].zfill(64)
    w3.eth.send_transaction({"from": mimin, "to": usdc, "data": data})
    
    abi_bal = [{"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
    c_bal = w3.eth.contract(address=usdc, abi=abi_bal)
    print(f"💰 SUCCESS! Whale Balance: {c_bal.functions.balanceOf(whale).call()/1e6} USDC")

except Exception as e:
    print(f"Failed to find Mimin: {e}")

