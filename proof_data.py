import requests
import json

url = "https://yields.llama.fi/pools"
response = requests.get(url)
data = response.json().get("data", [])

# Cari pool Aerodrome di Base yang APY-nya paling gila
aero_pools = [p for p in data if p.get("project") == "aerodrome-slipstream" and p.get("chain") == "Base"]
aero_pools = sorted(aero_pools, key=lambda x: x.get("apy", 0), reverse=True)

print(f"--- REAL-TIME DEFILLAMA DATA ---")
for p in aero_pools[:5]:
    print(f"Pool: {p.get('symbol')} | APY: {p.get('apy'):.2f}% | TVL: ${p.get('tvlUsd'):,.0f}")
