import asyncio
from web3 import Web3

# 1. Konek Pake WSS (WebSocket Secure), Bukan HTTP Biasa
# Ini ibarat lu naruh "Kuping" langsung nempel di tembok Blockchain Base
# (Note: Ini butuh API Key Alchemy/Infura yang WSS)
WSS_URL = "wss://base-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY" 
w3 = Web3(Web3.WebsocketProvider(WSS_URL))

# Alamat Pool yang mau kita pantau (Misal: Aerodrome WETH/USDC)
TARGET_POOL = "0xd0b53D9277642d2a2b0a9697b0624470A59647e7"
DANGER_THRESHOLD = 50000 * 10**6 # Kalau ada yang tarik liquidity > 50rb USDC

async def listen_for_danger():
    """Bot jadi Satpam 24 Jam Non-Stop"""
    print(f"🥷 SNIPER MODE: Memantau Pool {TARGET_POOL} setiap MILIDETIK...")
    
    try:
        # 2. Bikin "Saringan" (Filter) khusus buat transaksi di Pool kita
        # Kita minta Blockchain ngasih tau kita SETIAP KALI ada blok baru
        block_filter = w3.eth.filter('latest')
        
        while True:
            # 3. Ambil data blok terbaru (di Base, ini tiap 2 detik!)
            new_blocks = block_filter.get_new_entries()
            
            for block_hash in new_blocks:
                block = w3.eth.get_block(block_hash, full_transactions=True)
                print(f"🧱 Blok Baru: {block.number} | Memeriksa {len(block.transactions)} transaksi...")
                
                # 4. Cek satu-satu transaksi di dalem blok itu
                for tx in block.transactions:
                    # Kalau transaksinya nuju ke Pool Aerodrome kita
                    if tx['to'] and tx['to'].lower() == TARGET_POOL.lower():
                        # Cek apakah ini transaksi "Tarik Dana Gede" (Withdraw / Burn)
                        # (Di dunia nyata kita baca Input Data / Logs-nya)
                        value_usd = tx['value'] / 1e18 # Contoh kasar
                        
                        if value_usd > DANGER_THRESHOLD:
                            print(f"🚨 BAHAYA! PAUS NARIK DANA: {value_usd} USD!")
                            print(f"💥 EKSEKUSI PANIC SELL / WITHDRAW DETIK INI JUGA!")
                            await panic_withdraw()
                            
            # Tidur super sebentar biar CPU nggak meledak
            await asyncio.sleep(0.5) 
            
    except Exception as e:
        print(f"Koneksi WSS Putus: {e}")

async def panic_withdraw():
    """Fungsi Darurat: Tarik semua dana kita ke dompet dalam 1 blok"""
    print("🏃‍♂️ MENGIRIM TRANSAKSI WITHDRAW DENGAN GAS MAXIMAL (PRIORITY FEE TINGGI)!")
    # Logika Smart Contract execute_withdraw() masuk sini...
    # Transaksi lu bakal masuk blok berikutnya, selamat dari kehancuran Pool.
    
# Jalanin Satpam-nya
if __name__ == "__main__":
    print("Contoh Konsep Event-Driven Bot (Sniper/MEV)")
    # asyncio.run(listen_for_danger()) # (Di-comment karena butuh API Key WSS asli)
