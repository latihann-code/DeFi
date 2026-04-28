#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

echo "1. Mematikan sisa proses lama..."
pkill -9 anvil || true
pkill -f the_pilot_loop.py || true
pkill -f marathon_watchdog.py || true
sleep 3

echo "2. Menyalakan Anvil Base Fork (Port 8545)..."
nohup anvil --fork-url https://base-mainnet.g.alchemy.com/v2/1Y0eo6BirUXkg7TK3CBHe --chain-id 8453 --port 8545 > anvil.log 2>&1 &

echo "Tunggu Anvil siap (15 detik)..."
sleep 15

echo "3. Mengeksekusi Funding $5 USDC..."
python3 fund_robust.py > fund.log 2>&1
cat fund.log

echo "4. Menjalankan Agent PURE MODE..."
nohup python3 the_pilot_loop.py > pure_agent.log 2>&1 &
echo "DONE! Cek pure_agent.log untuk hasil."
