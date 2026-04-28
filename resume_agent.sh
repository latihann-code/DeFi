#!/bin/bash
# 1. Pastikan folder src masuk path
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

echo "🛡️ Memulai Pemulihan Agent..."

# 2. Cek apakah Anvil nyala, kalau mati nyalain
if ! pgrep anvil > /dev/null
then
    echo "🚀 Anvil mati, menyalakan ulang..."
    nohup anvil --fork-url https://mainnet.base.org --chain-id 8453 --port 8545 > anvil.log 2>&1 &
    sleep 10
else
    echo "✅ Anvil sudah nyala."
fi

# 3. Suntik ulang saldo (Minter Mode)
echo "💸 Mengisi ulang saldo Whale dan Wallet dari state terakhir..."
python3 mint_usdc_final.py

# 4. Nyalain Bot
echo "🧙‍♂️ Menjalankan Agent di background..."
pkill -f the_pilot_loop.py || true
nohup python3 the_pilot_loop.py > pure_agent.log 2>&1 &

echo "✅ SEMUA BERES! Bot sudah jalan lagi."
echo "Cek saldo terakhir di: predator_state.json"
