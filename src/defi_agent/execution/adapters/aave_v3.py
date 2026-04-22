from defi_agent.execution.adapters.base import BaseAdapter, TxData

class AaveV3Adapter(BaseAdapter):
    # Alamat Mainnet Aave V3 Pool (Default)
    POOL_ADDRESS = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"

    def encode_deposit(self, asset_address: str, amount: int) -> TxData:
        """
        Encode supply(asset, amount, onBehalfOf, referralCode)
        """
        # Dalam implementasi asli, kita akan menggunakan:
        # contract.functions.supply(asset, amount, my_address, 0).build_transaction()
        # Untuk mockup, kita buat string data dummy yang mewakili fungsi supply
        dummy_data = f"0x617ba037{asset_address[2:].zfill(64)}{hex(amount)[2:].zfill(64)}"
        
        return TxData(
            to=self.POOL_ADDRESS,
            data=dummy_data,
            gas_limit=250000
        )

    def encode_withdraw(self, asset_address: str, amount: int) -> TxData:
        """
        Encode withdraw(asset, amount, to)
        """
        dummy_data = f"0x69328dec{asset_address[2:].zfill(64)}{hex(amount)[2:].zfill(64)}"
        
        return TxData(
            to=self.POOL_ADDRESS,
            data=dummy_data,
            gas_limit=300000
        )

    def encode_approve(self, asset_address: str, spender_address: str, amount: int) -> TxData:
        """
        Standard ERC20 Approve.
        """
        dummy_data = f"0x095ea7b3{spender_address[2:].zfill(64)}{hex(amount)[2:].zfill(64)}"
        
        return TxData(
            to=asset_address,
            data=dummy_data,
            gas_limit=60000
        )
