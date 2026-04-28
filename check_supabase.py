import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("No Supabase URL/Key found.")
else:
    client = create_client(url, key)
    try:
        res = client.table("trades").select("*").execute()
        trades = res.data
        print(f"Total trades logged: {len(trades)}")
        for t in trades:
            print(f"- {t['action']} {t['amount']} {t['asset']} on {t['protocol']} (Status: {t['status']})")
            
        res_hb = client.table("heartbeat_logs").select("*", count="exact").execute()
        print(f"Total heartbeats logged: {res_hb.count}")
    except Exception as e:
        print(f"Error querying supabase: {e}")
