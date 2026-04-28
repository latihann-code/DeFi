from web3 import Web3
from defi_agent.execution.adapters.base import BaseAdapter, TxData

class UniswapV3Adapter(BaseAdapter):
    # Standard Uniswap V3 SwapRouter (Mainnet, Arbitrum, Optimism, Polygon)
    ROUTER_ADDRESS = "0xE592427A0AEce92De3Edee1F18E0157C05861564"

    ROUTER_ABI = [
        {"inputs": [{"components": [{"name": "tokenIn", "type": "address"}, {"name": "tokenOut", "type": "address"}, {"name": "fee", "type": "uint24"}, {"name": "recipient", "type": "address"}, {"name": "deadline", "type": "uint256"}, {"name": "amountIn", "type": "uint256"}, {"name": "amountOutMinimum", "type": "uint256"}, {"name": "sqrtPriceLimitX96", "type": "uint160"}], "name": "params", "type": "tuple"}], "name": "exactInputSingle", "outputs": [{"name": "amountOut", "type": "uint256"}], "stateMutability": "payable", "type": "function"}
    ]

    ERC20_ABI = [
        {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"}
    ]

    def encode_swap(self, token_in: str, token_out: str, amount_in: int, min_amount_out: int, recipient: str, fee: int = 3000) -> TxData:
        w3 = Web3()
        router = w3.eth.contract(address=Web3.to_checksum_address(self.ROUTER_ADDRESS), abi=self.ROUTER_ABI)
        deadline = 9999999999
        params = (
            Web3.to_checksum_address(token_in),
            Web3.to_checksum_address(token_out),
            fee,
            Web3.to_checksum_address(recipient),
            deadline,
            amount_in,
            min_amount_out,
            0
        )
        data = router.encode_abi("exactInputSingle", [params])
        return TxData(to=self.ROUTER_ADDRESS, data=data, gas_limit=250000)

    def encode_deposit(self, asset_address: str, amount: int, min_amount_out: int = 0) -> TxData:
        raise NotImplementedError("Uniswap V3 Adapter tidak mendukung deposit langsung.")

    def encode_withdraw(self, asset_address: str, amount: int, min_amount_out: int = 0) -> TxData:
        raise NotImplementedError("Uniswap V3 Adapter tidak mendukung withdraw langsung.")

    def encode_approve(self, asset_address: str, spender_address: str, amount: int) -> TxData:
        w3 = Web3()
        erc20 = w3.eth.contract(address=Web3.to_checksum_address(asset_address), abi=self.ERC20_ABI)
        data = erc20.encode_abi("approve", [Web3.to_checksum_address(spender_address), amount])
        return TxData(to=Web3.to_checksum_address(asset_address), data=data, gas_limit=60000)
