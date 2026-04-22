from typing import Dict
from defi_agent.execution.adapters.base import BaseAdapter, TxData

class AdapterEngine:
    def __init__(self):
        self.adapters: Dict[str, BaseAdapter] = {}

    def register_adapter(self, protocol_name: str, adapter: BaseAdapter):
        self.adapters[protocol_name.lower()] = adapter

    def get_tx_data(self, protocol_name: str, action: str, params: dict) -> TxData:
        """
        Dispatcher utama untuk mengambil data transaksi berdasarkan protokol dan aksi.
        """
        adapter = self.adapters.get(protocol_name.lower())
        if not adapter:
            raise ValueError(f"Protokol {protocol_name} belum terdaftar.")
            
        action = action.upper()
        if action == "DEPOSIT":
            return adapter.encode_deposit(params["asset"], params["amount"])
        elif action == "WITHDRAW":
            return adapter.encode_withdraw(params["asset"], params["amount"])
        elif action == "APPROVE":
            return adapter.encode_approve(params["asset"], params["spender"], params["amount"])
        else:
            raise ValueError(f"Aksi {action} tidak didukung.")
