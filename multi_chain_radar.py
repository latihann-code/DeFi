import logging
from dotenv import load_dotenv
from defi_agent.ingestion.scanner import MultiChainScanner
from defi_agent.memory import DatabaseManager

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Radar")

def main():
    load_dotenv()
    logger.info("📡 STARTING MULTI-CHAIN RADAR...")
    
    scanner = MultiChainScanner()
    db = DatabaseManager()
    
    # 1. SCAN GLOBAL
    opportunities = scanner.get_best_opportunities(min_tvl=1_000_000)
    
    print("\n🗺️ --- MULTI-CHAIN TREASURE MAP ---")
    print(f"{'CHAIN':<12} | {'PROJECT':<15} | {'APY':<10} | {'TVL':<15}")
    print("-" * 60)
    
    for opp in opportunities:
        print(f"{opp['chain_name']:<12} | {opp['project']:<15} | {opp['apy']:>8.2f}% | ${opp['tvl']:>13,.0f}")
        
        # 2. LOG KE SUPABASE (Otomatis masuk ke 'heartbeat_logs' sebagai benchmark)
        db.log_heartbeat(
            status=f"Scan-{opp['chain']}",
            heartbeat_seconds=0,
            best_opportunity=f"{opp['project']} ({opp['pool']})",
            best_apy=opp['apy']
        )
    
    # 3. MIGRATION ADVICE (Simulasi Modal $5)
    capital = 5.0
    best_overall = opportunities[0]
    # Anggap kita sekarang di Arbitrum
    advice = scanner.migration_advice("arbitrum", best_overall, capital)
    
    print("\n🧠 --- PREDATOR INSIGHT ($5 CAPITAL) ---")
    print(f"Target Terbaik: {best_overall['project']} on {best_overall['chain_name']} ({best_overall['apy']:.2f}% APY)")
    print(f"Keputusan: {advice['action']}")
    print(f"Alasan: {advice['reason']}")

if __name__ == "__main__":
    main()
