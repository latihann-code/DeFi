from web3 import Web3
import time

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
whale = Web3.to_checksum_address("0x70997970C51812dc3A010C7d01b50e0d17dc79C8")
usdc = Web3.to_checksum_address("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
router = Web3.to_checksum_address("0x2626664c39fB33923406f47A0925761F6C0811B1") # Universal Router Base

def swap():
    # 1. Kasih ETH buat belanja
    w3.provider.make_request("anvil_setBalance", [whale, hex(w3.to_wei(100, "ether"))])
    
    # 2. Cari Sultan USDC beneran di Fork ini buat kita "rampok" lewat impersonate
    # Kita pake Pool Uniswap V3 WETH/USDC (biasanya isinya melimpah)
    pool_uniswap = Web3.to_checksum_address("0xd0b53D9277642d2a2b0a9697b0624470A59647e7")
    
    w3.provider.make_request("anvil_setBalance", [pool_uniswap, hex(w3.to_wei(10, "ether"))])
    w3.provider.make_request("anvil_impersonateAccount", [pool_uniswap])
    
    abi = [{"constant": False, "inputs": [{"name": "to", "type": "address"}, {"name": "value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"},
           {"constant": True, "inputs": [{"name": "owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}]
    c = w3.eth.contract(address=usdc, abi=abi)
    
    # Kita coba paksa transfer dari pool ke whale
    # Kalo pool 0, kita coba Circle (Sultan Base)
    circle = Web3.to_checksum_address("0x3300f17e6988C64348409409B1133c8711883585")
    w3.provider.make_request("anvil_impersonateAccount", [circle])
    w3.provider.make_request("anvil_setBalance", [circle, hex(w3.to_wei(1, "ether"))])

    try:
        # Coba ambil dari Circle (biasanya di Base Sultan USDC itu alamat Circle)
        # Kita brute force transfer ampe dapet duitnya
        sources = [circle, pool_uniswap, "0x43063852079031c50e0513e9a409409B1133c871"]
        for src in sources:
            src_addr = Web3.to_checksum_address(src)
            w3.provider.make_request("anvil_impersonateAccount", [src_addr])
            try:
                # Kita coba transfer dikit dulu
                c.functions.transfer(whale, 100000 * 10**6).transact({'from': src_addr})
                print(f"✅ Dapet USDC dari {src}!")
                break
            except: pass
    except: pass

    print(f"Final Whale Balance: {c.functions.balanceOf(whale).call()/1e6} USDC")

if __name__ == "__main__":
    swap()
