import asyncio
import websockets
import json

async def test_ws():
    uri = "wss://api.llama.fi/ws"  # DefiLlama doesn't officially have a public WS for prices, but let's check
    try:
        async with websockets.connect(uri) as ws:
            print("Connected to DefiLlama WS!")
            await ws.send(json.dumps({"action": "subscribe", "channel": "prices", "coins": ["base:0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"]}))
            response = await asyncio.wait_for(ws.recv(), timeout=5)
            print(f"Response: {response}")
    except Exception as e:
        print(f"WS Test Failed: {e}")

asyncio.run(test_ws())
