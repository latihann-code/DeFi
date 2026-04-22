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
    def encode_deposit(self, asset_address: str, amount: int) -> TxData:
        """Encode fungsi deposit ke smart contract."""
        pass

    @abstractmethod
    def encode_withdraw(self, asset_address: str, amount: int) -> TxData:
        """Encode fungsi withdraw dari smart contract."""
        pass

    @abstractmethod
    def encode_approve(self, asset_address: str, spender_address: str, amount: int) -> TxData:
        """Standard ERC20 Approve."""
        pass
