import pytest
from unittest.mock import MagicMock
from defi_agent.execution.engine import AdapterEngine
from defi_agent.execution.adapters.base import BaseAdapter, TxData

class MockAdapter(BaseAdapter):
    def encode_deposit(self, asset, amount): return TxData("0x1", "deposit_data")
    def encode_withdraw(self, asset, amount): return TxData("0x1", "withdraw_data")
    def encode_approve(self, asset, spender, amount): return TxData("0x2", "approve_data")
    def encode_swap(self, token_in, token_out, amount_in, min_amount_out): return TxData("0x3", "swap_data")

def test_adapter_engine_registration():
    engine = AdapterEngine()
    engine.register_adapter("aave", MockAdapter())
    
    # Test valid dispatch
    tx = engine.get_tx_data("aave", "deposit", {"asset": "USDC", "amount": 100})
    assert tx.data == "deposit_data"
    assert tx.to == "0x1"

def test_adapter_engine_invalid_protocol():
    engine = AdapterEngine()
    with pytest.raises(ValueError, match="belum terdaftar"):
        engine.get_tx_data("unknown", "deposit", {})
