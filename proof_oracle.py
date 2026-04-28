from the_pilot_loop import SevenDayPredator
import os

# Setup environment
os.environ["RPC_URL"] = "http://127.0.0.1:8545"
agent = SevenDayPredator()

print("\n--- 🧪 TESTING HYBRID ORACLE ---")
# Aerodrome WETH/USDC Pool
pool_addr = "0xd0b53D9277642d2a2b0a9697b0624470A59647e7"
price = agent.get_onchain_price(pool_addr)

if price:
    print(f"✅ RPC SUCCESS! Raw Price Ratio from Pool: {price}")
else:
    print("⚠️ RPC Failed (as expected in fork), testing API Fallback...")
    # Test Fallback (WETH & USDC)
    prices = agent.get_real_prices(["0x4200000000000000000000000000000000000006", "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"])
    if prices:
        print(f"✅ API FALLBACK SUCCESS! Real Prices: {prices}")
    else:
        print("❌ Both RPC and API Failed. Check connection.")
