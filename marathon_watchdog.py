import subprocess
import time
import os
import requests

def is_anvil_up(port):
    try:
        res = requests.post(f"http://127.0.0.1:{port}", json={"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}, timeout=2)
        return res.status_code == 200
    except:
        return False

def start_anvil(port):
    print(f"🚀 Starting Anvil on port {port}...")
    cmd = f"anvil --fork-url https://base-mainnet.g.alchemy.com/v2/1Y0eo6BirUXkg7TK3CBHe --chain-id 8453 --port {port} --no-mining --order fifo"
    with open("anvil_marathon.log", "a") as f:
        return subprocess.Popen(cmd.split(), stdout=f, stderr=f)

def run_funding():
    print("💰 Running Auto-Funding ($5 USDC)...")
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{env.get('PYTHONPATH', '')}:{os.getcwd()}/src"
    subprocess.run(["python3", "force_fund.py"], env=env)

def start_agent():
    print("🦾 Starting Pure Agent...")
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{env.get('PYTHONPATH', '')}:{os.getcwd()}/src"
    with open("pure_agent.log", "a") as f:
        return subprocess.Popen(["python3", "the_pilot_loop.py"], env=env, stdout=f, stderr=f)

def marathon():
    port = 8545
    anvil_proc = None
    agent_proc = None

    while True:
        # 1. Check Anvil
        if not is_anvil_up(port):
            print("⚠️ Anvil is down or not responding. Restarting...")
            if anvil_proc: anvil_proc.terminate()
            anvil_proc = start_anvil(port)
            time.sleep(15) # Wait for boot
            run_funding()
        
        # 2. Check Agent
        if agent_proc is None or agent_proc.poll() is not None:
            print("⚠️ Agent is down. Restarting...")
            agent_proc = start_agent()
        
        time.sleep(30) # Check every 30 seconds

if __name__ == "__main__":
    marathon()
