import requests

try:
    print("Mencari data langsung dari API DefiLlama (yields.llama.fi/pools)...")
    response = requests.get("https://yields.llama.fi/pools", timeout=10)
    data = response.json().get("data", [])
    
    # Filter untuk project yang mengandung nama "aerodrome"
    aero_pools = [p for p in data if p.get("project") and "aerodrome" in p.get("project").lower() and p.get("chain", "").lower() == "base"]
    
    # Sort berdasarkan APY paling tinggi
    aero_pools_sorted = sorted(aero_pools, key=lambda x: x.get("apy", 0), reverse=True)
    
    print("\n--- TOP 10 YIELDS AERODROME (BASE) SAAT INI ---")
    print(f"{'Pool':<20} | {'Project':<20} | {'APY':<10} | {'TVL (USD)':<15}")
    print("-" * 75)
    
    for p in aero_pools_sorted[:10]:
        symbol = p.get('symbol', 'Unknown')
        project = p.get('project', 'Unknown')
        apy = p.get('apy', 0)
        tvl = p.get('tvlUsd', 0)
        print(f"{symbol:<20} | {project:<20} | {apy:>8.2f}% | ${tvl:,.0f}")
        
except Exception as e:
    print(f"Error fetching data: {e}")
