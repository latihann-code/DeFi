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

    def __init__(self, chain: str = "ethereum"):
        self.chain = chain.lower()
        self.pool_address = self.POOL_ADDRESSES.get(self.chain, self.POOL_ADDRESSES["ethereum"])

    def encode_deposit(self, asset_address: str, amount: int) -> TxData:
        """
        Encode supply(asset, amount, onBehalfOf, referralCode)
        Selector: 0x617ba037
        """
        # Kita pakai dummy encoding untuk demo, di sistem live gunakan web3.contract
        p_asset = asset_address[2:].zfill(64)
        p_amount = hex(amount)[2:].zfill(64)
        # onBehalfOf dummy (akan diganti oleh manager)
        p_on_behalf = "0".zfill(64)
        p_referral = "0".zfill(64)
        
        data = f"0x617ba037{p_asset}{p_amount}{p_on_behalf}{p_referral}"
        
        return TxData(
            to=self.pool_address,
            data=data,
            gas_limit=250000
        )

    def encode_withdraw(self, asset_address: str, amount: int) -> TxData:
        p_asset = asset_address[2:].zfill(64)
        p_amount = hex(amount)[2:].zfill(64)
        p_to = "0".zfill(64)
        data = f"0x69328dec{p_asset}{p_amount}{p_to}"
        return TxData(to=self.pool_address, data=data, gas_limit=300000)

    def encode_approve(self, asset_address: str, spender_address: str, amount: int) -> TxData:
        p_spender = spender_address[2:].zfill(64)
        p_amount = hex(amount)[2:].zfill(64)
        data = f"0x095ea7b3{p_spender}{p_amount}"
        return TxData(to=asset_address, data=data, gas_limit=60000)

    def encode_swap(self, *args, **kwargs) -> TxData:
        raise NotImplementedError("Aave V3 Adapter tidak mendukung swap langsung.")
