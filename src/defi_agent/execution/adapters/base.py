from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class TxData:
    to: str
    data: str
    value: int = 0
    gas_limit: Optional[int] = None

class BaseAdapter(ABC):
    @abstractmethod
    def encode_deposit(self, asset_address: str, amount: int, min_amount_out: int = 0) -> TxData:
        """Encode fungsi deposit ke smart contract."""
        pass

    @abstractmethod
    def encode_withdraw(self, asset_address: str, amount: int, min_amount_out: int = 0) -> TxData:
        """Encode fungsi withdraw dari smart contract."""
        pass

    @abstractmethod
    def encode_approve(self, asset_address: str, spender_address: str, amount: int) -> TxData:
        """Standard ERC20 Approve."""
        pass

    @abstractmethod
    def encode_swap(self, token_in: str, token_out: str, amount_in: int, min_amount_out: int, recipient: str, fee: int = 3000) -> TxData:
        """Encode fungsi swap/trade."""
        pass
