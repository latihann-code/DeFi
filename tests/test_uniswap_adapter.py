from defi_agent.execution.adapters.uniswap_v3 import UniswapV3Adapter

def test_uniswap_v3_swap_encoding():
    adapter = UniswapV3Adapter()
    
    token_in = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48" # USDC
    token_out = "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1" # WETH (Arbitrum)
    amount_in = 1000 * 10**6
    min_amount_out = 0
    recipient = "0x0D70fAff30ad1FeCbB2F3d20E20e1dfD50fFF30d"
    
    tx_data = adapter.encode_swap(token_in, token_out, amount_in, min_amount_out, recipient)
    
    print(f"\n✅ Uniswap Swap Tx Data: {tx_data.data[:64]}...")
    assert tx_data.to == adapter.ROUTER_ADDRESS
    assert tx_data.data.startswith("0x414bf389") # Selector exactInputSingle
    assert len(tx_data.data) > 100

if __name__ == "__main__":
    test_uniswap_v3_swap_encoding()
    print("Uniswap V3 Adapter Test: PASSED!")
