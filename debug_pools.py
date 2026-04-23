from defi_agent.ingestion.scanner import MultiChainScanner
import json

def main():
    scanner = MultiChainScanner()
    data = scanner.scan_all_chains()
    
    print("\n🔍 DEBUGGING POOLS...")
    for chain, pools in data.items():
        if chain in ["base", "arbitrum"]:
            print(f"\n--- {chain.upper()} ---")
            found = [p for p in pools if "aave" in p.project.lower()]
            for f in found:
                print(f"Project: {f.project} | Symbol: {f.underlying_tokens} | TVL: ${f.tvl_usd:,.0f} | APY: {f.apy}%")

if __name__ == "__main__":
    main()
