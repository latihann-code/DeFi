import os
from supabase import create_client, Client
from dotenv import load_dotenv
import json

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

client = create_client(url, key)

print("--- HEARBEAT LOGS ---")
res = client.table("heartbeat_logs").select("*").order("created_at", desc=True).limit(5).execute()
for r in res.data:
    print(r['created_at'], " | Best APY: ", r['best_apy'])

print("\n--- TRADES ---")
res = client.table("trades").select("*").order("created_at", desc=True).limit(5).execute()
for r in res.data:
    print(r['created_at'], " | ", r['action'], r['amount'], "on", r['protocol'])

