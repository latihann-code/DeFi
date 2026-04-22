import pytest
from unittest.mock import MagicMock, patch
from web3 import Web3
from defi_agent.execution.manager import TransactionManager
from defi_agent.execution.engine import AdapterEngine
from defi_agent.execution.adapters.aave_v3 import AaveV3Adapter

@pytest.fixture
def full_setup():
    # Mock Web3
    w3 = MagicMock(spec=Web3)
    w3.eth = MagicMock()
    w3.eth.get_transaction_count.return_value = 100
    w3.eth.chain_id = 1
    w3.eth.get_block.return_value = {"baseFeePerGas": 10**9}
    w3.eth.estimate_gas.return_value = 250000
    w3.to_wei = Web3.to_wei
    
    # Manager
    manager = TransactionManager(w3, "0x" + "1"*64, "0x" + "2"*40)
    
    # Engine & Adapter
    engine = AdapterEngine()
    engine.register_adapter("aave", AaveV3Adapter())
    
    return manager, engine

@patch("web3.eth.Eth.account.sign_transaction")
def test_full_execution_flow(mock_sign, full_setup):
    manager, engine = full_setup
    
    # 1. Brain memutuskan DEPOSIT ke Aave
    action = "DEPOSIT"
    params = {"asset": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "amount": 1000}
    
    # 2. Ambil data transaksi dari Adapter
    tx_data = engine.get_tx_data("aave", action, params)
    
    # 3. Kirim via Transaction Manager
    mock_signed = MagicMock()
    mock_signed.raw_transaction = b"signed"
    manager.w3.eth.account.sign_transaction.return_value = mock_signed
    manager.w3.eth.send_raw_transaction.return_value = Web3.to_bytes(hexstr="0xfeed")
    
    tx_dict = {
        "to": tx_data.to,
        "data": tx_data.data,
        "gas": tx_data.gas_limit
    }
    tx_hash = manager.send_transaction(tx_dict)
    
    assert tx_hash == "0x000000000000000000000000000000000000000000000000000000000000feed"
    assert manager.nonce == 101
    print(f"\n✅ Full Execution Flow Verified: {action} on Aave")
