import pytest
from unittest.mock import MagicMock, patch
from web3 import Web3
from defi_agent.execution.manager import TransactionManager

@pytest.fixture
def mock_w3():
    w3 = MagicMock(spec=Web3)
    w3.eth = MagicMock()
    w3.eth.get_transaction_count.return_value = 10
    w3.eth.chain_id = 1
    w3.eth.get_block.return_value = {"baseFeePerGas": 20000000000} # 20 Gwei
    w3.to_wei = Web3.to_wei
    return w3

def test_tx_manager_init(mock_w3):
    manager = TransactionManager(mock_w3, "0x" + "1"*64, "0x" + "2"*40)
    assert manager.nonce == 10
    assert Web3.is_address(manager.address)

def test_get_gas_strategy(mock_w3):
    manager = TransactionManager(mock_w3, "0x" + "1"*64, "0x" + "2"*40)
    strategy = manager.get_gas_strategy(priority="high")
    assert "maxFeePerGas" in strategy
    assert "maxPriorityFeePerGas" in strategy
    # High priority tip = 3 Gwei
    assert strategy["maxPriorityFeePerGas"] == 3000000000

@patch("web3.eth.Eth.account.sign_transaction")
def test_send_transaction(mock_sign, mock_w3):
    # Setup mock signing
    mock_signed = MagicMock()
    mock_signed.raw_transaction = b"signed_tx"
    mock_w3.eth.account.sign_transaction.return_value = mock_signed
    mock_w3.eth.send_raw_transaction.return_value = Web3.to_bytes(hexstr="0xabc")
    mock_w3.eth.estimate_gas.return_value = 21000
    
    manager = TransactionManager(mock_w3, "0x" + "1"*64, "0x" + "2"*40)
    tx = {"to": "0x" + "3"*40, "value": 1000}
    
    tx_hash = manager.send_transaction(tx)
    
    assert "abc" in tx_hash
    assert manager.nonce == 11 # Nonce should increment
    mock_w3.eth.send_raw_transaction.assert_called_once()
