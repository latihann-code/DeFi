import os
from dotenv import load_dotenv
from web3 import Web3

def main():
    load_dotenv()
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    wallet_address = Web3.to_checksum_address(os.getenv("WALLET_ADDRESS"))
    usdc_address = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
    
    # Whale: Base USDC Proxy (biasanya punya balance buat dikelola)
    whale = Web3.to_checksum_address("0x330E661f4356E87889A1201D86b3602f3C57973B")
    
    w3.provider.make_request("anvil_setBalance", [wallet_address, hex(w3.to_wei(10, "ether"))])
    w3.provider.make_request("anvil_impersonateAccount", [whale])
    w3.provider.make_request("anvil_setBalance", [whale, hex(w3.to_wei(1, "ether"))])

    # Kita paksa balance whale jadi gede dulu (Slot 0 di proxy biasanya)
    w3.provider.make_request("anvil_setStorageAt", [usdc_address, hex(0), hex(10**18).zfill(64)])

    usdc_abi = [{"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"}, {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"}]
    usdc_contract = w3.eth.contract(address=usdc_address, abi=usdc_abi)

    try:
        w3.eth.send_transaction({
            "from": whale,
            "to": usdc_address,
            "data": usdc_contract.encode_abi("transfer", [wallet_address, 100 * 10**6]),
            "gas": 100000
        })
    except:
        pass

    print(f"💰 Wallet Balance: {usdc_contract.functions.balanceOf(wallet_address).call() / 10**6} USDC")

if __name__ == "__main__":
    main()
