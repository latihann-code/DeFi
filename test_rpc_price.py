from web3 import Web3
import math

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Aerodrome Slipstream WETH/USDC Pool
pool_address = Web3.to_checksum_address("0xd0b53D9277642d2a2b0a9697b0624470A59647e7")

# Minimal ABI for slot0
abi = [
    {
        "inputs": [],
        "name": "slot0",
        "outputs": [
            {"internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"},
            {"internalType": "int24", "name": "tick", "type": "int24"},
            {"internalType": "uint16", "name": "observationIndex", "type": "uint16"},
            {"internalType": "uint16", "name": "observationCardinality", "type": "uint16"},
            {"internalType": "uint16", "name": "observationCardinalityNext", "type": "uint16"},
            {"internalType": "uint8", "name": "feeProtocol", "type": "uint8"},
            {"internalType": "bool", "name": "unlocked", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

def get_price():
    if not w3.is_connected():
        print("RPC disconnected")
        return
        
    contract = w3.eth.contract(address=pool_address, abi=abi)
    try:
        slot0 = contract.functions.slot0().call()
        sqrtPriceX96 = slot0[0]
        
        # Price calculation for UniV3: (sqrtPriceX96 / 2^96)^2
        # Adjusting for decimals (WETH: 18, USDC: 6)
        price_raw = (sqrtPriceX96 / (2**96)) ** 2
        # Decimals adjustment: price_raw * 10^(decimals_token0 - decimals_token1)
        # Token0 is USDC (6), Token1 is WETH (18) -> diff is -12
        # price = price_raw * 10**12
        # Wait, usually token0 is the one with lower address.
        # USDC: 0x8335... , WETH: 0x4200... -> WETH is token0, USDC is token1
        # price = (1 / price_raw) * 10**(18-6)
        
        print(f"✅ RPC Connected! Block: {w3.eth.block_number}")
        print(f"Pool: {pool_address}")
        print(f"sqrtPriceX96: {sqrtPriceX96}")
        
        # Simple ratio
        ratio = (sqrtPriceX96 ** 2) / (2 ** 192)
        # Adjust for USDC (6) and WETH (18)
        # If token0=WETH, token1=USDC -> price = ratio * 10^18 / 10^6
        # Let's just output the raw ratio first
        print(f"Raw Ratio: {ratio}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

get_price()
