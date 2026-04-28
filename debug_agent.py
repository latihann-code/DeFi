from the_pilot_loop import SevenDayPredator
import os

os.environ["RPC_URL"] = "http://127.0.0.1:8545"
agent = SevenDayPredator()
print("--- 1. Testing Sync ---")
agent.sync_capital_from_chain()
print(f"Capital: {agent.capital}")

print("--- 2. Testing Market Sync ---")
all_pools = agent.client.fetch_yields()
print(f"Fetched {len(all_pools)} pools")

if agent.current_pool:
    fresh_data = next((p for p in all_pools if p.project == agent.current_pool.project and p.chain.lower() == agent.current_chain), None)
    if fresh_data:
        print(f"Fresh APY: {fresh_data.apy}")
        
print("--- 3. Testing Real Price ---")
prices = agent.get_real_prices(["0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", "0xbF927b841994731C573BDF09ceB0c6B0Aa887cDd"])
print(f"Prices: {prices}")
