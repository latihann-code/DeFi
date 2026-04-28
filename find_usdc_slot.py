from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
usdc = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
# Holder yang kita tau ada isinya di mainnet (Aerodrome Pool)
holder = Web3.to_checksum_address("0xf89d7b9CB797c61106122839497d4937034d1c97")

for s in range(100):
    idx = w3.keccak(hexstr=holder[2:].zfill(64) + hex(s)[2:].zfill(64))
    val = w3.eth.get_storage_at(usdc, idx)
    if int(val.hex(), 16) > 0:
        print(f"FOUND SLOT: {s} | Value: {int(val.hex(), 16)}")
