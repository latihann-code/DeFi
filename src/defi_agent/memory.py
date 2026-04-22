import os
from supabase import create_client, Client

class DatabaseManager:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            print("⚠️ SUPABASE_URL atau SUPABASE_KEY tidak ditemukan di .env")
            self.client = None
        else:
            self.client = create_client(url, key)

    def log_trade(self, protocol, action, asset, amount, tx_hash, status, risk_score, reason):
        if not self.client: return
        try:
            data = {
                "protocol": protocol,
                "action": action,
                "asset": asset,
                "amount": amount,
                "tx_hash": tx_hash,
                "status": status,
                "risk_score": risk_score,
                "reason": reason
            }
            self.client.table("trades").insert(data).execute()
        except Exception as e:
            print(f"❌ Gagal log trade ke Supabase: {e}")

    def log_heartbeat(self, status, heartbeat_seconds, best_opportunity, best_apy):
        if not self.client: 
            print("⚠️ Supabase Client NOT initialized.")
            return
        try:
            print(f"📡 Sending heartbeat to Supabase: {best_opportunity}...")
            data = {
                "status": status,
                "heartbeat_seconds": heartbeat_seconds,
                "best_opportunity": best_opportunity,
                "best_apy": best_apy
            }
            res = self.client.table("heartbeat_logs").insert(data).execute()
            print("✅ Supabase Log Success!")
        except Exception as e:
            print(f"❌ Gagal log heartbeat ke Supabase: {e}")
