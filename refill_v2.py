from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
whale = Web3.to_checksum_address("0xcfA3Ef56d303AE4fAabA0592388F19d7C3399FB4")
usdc_address = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")

# Holder raksasa yang pasti ada isinya di Base Mainnet
real_whale = Web3.to_checksum_address("0x3300f17e6988C64348409409B1133c8711883585") # Circle

def main():
    # 1. Coba pake slot storage Circle (biasanya slot 0 di Proxy, atau slot 9)
    # Tapi cara paling gampang: Ambil dari Account raksasa mainnet
    # Kita cari holder top dari CoinMarketCap/Etherscan Base
    holders = [
        "0x3300f17e6988C64348409409B1133c8711883585",
        "0x0000000000000000000000000000000000000000",
        "0x43063852079031c50e0513e9a409409B1133c871",
        "0x3D9E3b74Cb538D1996D2Bf871888d835284849fA" # Aerodrome Vault
    ]
    
    for h in holders:
        h_addr = Web3.to_checksum_address(h)
        w3.provider.make_request("anvil_setBalance", [h_addr, hex(w3.to_wei(1, "ether"))])
        w3.provider.make_request("anvil_impersonateAccount", [h_addr])
        
        abi = [{"constant": False, "inputs": [{"name": "to", "type": "address"}, {"name": "value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
               {"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
        contract = w3.eth.contract(address=usdc_address, abi=abi)
        
        try:
            bal = contract.functions.balanceOf(h_addr).call()
            if bal > 100000 * 10**6:
                print(f"Found balance in {h}: {bal / 1e6} USDC")
                contract.functions.transfer(whale, 1000000 * 10**6).transact({'from': h_addr})
                print(f"✅ Transferred from {h}")
                break
        except Exception as e:
            print(f"Error with {h}: {e}")
        w3.provider.make_request("anvil_stopImpersonatingAccount", [h_addr])

    print(f"Final Whale Balance: {contract.functions.balanceOf(whale).call() / 1e6} USDC")

if __name__ == "__main__":
    main()
