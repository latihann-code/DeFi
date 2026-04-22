from defi_agent.execution.adapters.base import BaseAdapter, TxData

class UniswapV3Adapter(BaseAdapter):
    # Standard Uniswap V3 SwapRouter (Mainnet, Arbitrum, Optimism, Polygon)
    ROUTER_ADDRESS = "0xE592427A0AEce92De3Edee1F18E0157C05861564"

    def encode_swap(self, token_in: str, token_out: str, amount_in: int, min_amount_out: int, recipient: str, fee: int = 3000) -> TxData:
        """
        Encode exactInputSingle(params) untuk swap satu jalur.
        params = (tokenIn, tokenOut, fee, recipient, deadline, amountIn, amountOutMinimum, sqrtPriceLimitX96)
        """
        # Function Selector untuk exactInputSingle((address,address,uint24,address,uint256,uint256,uint256,uint160))
        # Selector: 0x414bf389
        
        # Padding data manual (mockup encoding untuk demo)
        # Di sistem produksi, kita pake w3.eth.contract().encode_abi()
        deadline = 9999999999 # Jauh di masa depan
        
        # Encoding tuple params
        # (tokenIn, tokenOut, fee, recipient, deadline, amountIn, amountOutMinimum, sqrtPriceLimitX96)
        p_token_in = token_in[2:].zfill(64)
        p_token_out = token_out[2:].zfill(64)
        p_fee = hex(fee)[2:].zfill(64)
        p_recipient = recipient[2:].zfill(64)
        p_deadline = hex(deadline)[2:].zfill(64)
        p_amount_in = hex(amount_in)[2:].zfill(64)
        p_min_out = hex(min_amount_out)[2:].zfill(64)
        p_price_limit = "0".zfill(64)
        
        data = f"0x414bf389{p_token_in}{p_token_out}{p_fee}{p_recipient}{p_deadline}{p_amount_in}{p_min_out}{p_price_limit}"
        
        return TxData(
            to=self.ROUTER_ADDRESS,
            data=data,
            gas_limit=250000
        )

    # Implementasi method abstract (Wajib karena inherit dari BaseAdapter)
    def encode_deposit(self, asset_address: str, amount: int) -> TxData:
        raise NotImplementedError("Uniswap V3 Adapter tidak mendukung deposit langsung.")

    def encode_withdraw(self, asset_address: str, amount: int) -> TxData:
        raise NotImplementedError("Uniswap V3 Adapter tidak mendukung withdraw langsung.")

    def encode_approve(self, asset_address: str, spender_address: str, amount: int) -> TxData:
        """Standard ERC20 Approve untuk Router Uniswap."""
        dummy_data = f"0x095ea7b3{spender_address[2:].zfill(64)}{hex(amount)[2:].zfill(64)}"
        return TxData(to=asset_address, data=dummy_data, gas_limit=60000)
