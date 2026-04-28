import requests
import os
from web3 import Web3

# 1. Test RPC Connection
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
print(f"--- 🌐 BLOCKCHAIN STATUS ---")
print(f"Connected to Anvil: {w3.is_connected()}")
print(f"Current Block: {w3.eth.block_number}")

# 2. Test Real Price API (The Eye)
print(f"\n--- 👁️  REAL-TIME PRICE TEST ---")
# Token: WETH (Base), USDC (Base)
query = "base:0x4200000000000000000000000000000000000006,base:0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
url = f"https://coins.llama.fi/prices/current/{query}"
res = requests.get(url).json()

for k, v in res.get("coins", {}).items():
    print(f"Token: {k} | Price: ${v['price']}")

print("\n✅ Bot lu pake data harga ini buat ngitung IL!")
