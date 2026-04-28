from web3 import Web3
from defi_agent.execution.adapters.base import BaseAdapter, TxData

class AaveV3Adapter(BaseAdapter):
    # Mapping Pool Addresses per Chain
    POOL_ADDRESSES = {
        "ethereum": "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
        "arbitrum": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
        "base": "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5",
        "polygon": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
        "optimism": "0x794a61358D6845594F94dc1DB02A252b5b4814aD"
    }

    AAVE_ABI = [
        {"inputs": [{"name": "asset", "type": "address"}, {"name": "amount", "type": "uint256"}, {"name": "onBehalfOf", "type": "address"}, {"name": "referralCode", "type": "uint16"}], "name": "supply", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
        {"inputs": [{"name": "asset", "type": "address"}, {"name": "amount", "type": "uint256"}, {"name": "to", "type": "address"}], "name": "withdraw", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "nonpayable", "type": "function"}
    ]

    ERC20_ABI = [
        {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "type": "function"}
    ]

    def __init__(self, chain: str = "ethereum", wallet_address: str = "0x0000000000000000000000000000000000000000"):
        self.chain = chain.lower()
        self.pool_address = self.POOL_ADDRESSES.get(self.chain, self.POOL_ADDRESSES["ethereum"])
        self.wallet_address = Web3.to_checksum_address(wallet_address)
        self.w3 = Web3()
        self.contract = self.w3.eth.contract(address=self.pool_address, abi=self.AAVE_ABI)

    def encode_deposit(self, asset_address: str, amount: int, min_amount_out: int = 0) -> TxData:
        data = self.contract.encode_abi("supply", [Web3.to_checksum_address(asset_address), amount, self.wallet_address, 0])
        return TxData(to=self.pool_address, data=data, gas_limit=250000)

    def encode_withdraw(self, asset_address: str, amount: int, min_amount_out: int = 0) -> TxData:
        data = self.contract.encode_abi("withdraw", [Web3.to_checksum_address(asset_address), amount, self.wallet_address])
        return TxData(to=self.pool_address, data=data, gas_limit=300000)

    def encode_approve(self, asset_address: str, spender_address: str, amount: int) -> TxData:
        erc20 = self.w3.eth.contract(address=Web3.to_checksum_address(asset_address), abi=self.ERC20_ABI)
        data = erc20.encode_abi("approve", [Web3.to_checksum_address(spender_address), amount])
        return TxData(to=Web3.to_checksum_address(asset_address), data=data, gas_limit=60000)

    def encode_swap(self, *args, **kwargs) -> TxData:
        raise NotImplementedError("Aave V3 Adapter tidak mendukung swap langsung.")
