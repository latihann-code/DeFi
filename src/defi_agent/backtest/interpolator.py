import numpy as np

class HourlyInterpolator:
    def __init__(self, noise_std: float = 0.0):
        """
        Inisialisasi interpolator.
        :param noise_std: Standar deviasi dari Gaussian Noise yang akan ditambahkan.
        """
        self.noise_std = noise_std

    def generate_hourly(self, daily_data: list[dict], field_name: str) -> list[dict]:
        """
        Mengubah data harian menjadi per jam dengan linear interpolation + Gaussian noise.
        :param daily_data: List dictionary berisi 'timestamp' dan nilai (field_name).
        :param field_name: Nama field yang akan diinterpolasi (misal: 'apy').
        :return: List dictionary data per jam.
        """
        if not daily_data:
            return []
            
        hourly_results = []
        
        # Sort by timestamp to be safe
        data_sorted = sorted(daily_data, key=lambda x: x["timestamp"])
        
        for i in range(len(data_sorted) - 1):
            start_point = data_sorted[i]
            end_point = data_sorted[i+1]
            
            start_ts = start_point["timestamp"]
            end_ts = end_point["timestamp"]
            start_val = start_point[field_name]
            end_val = end_point[field_name]
            
            # Rentang waktu dalam detik
            duration_sec = end_ts - start_ts
            # Total jam (biasanya 24)
            total_hours = duration_sec // 3600
            
            for h in range(total_hours):
                current_ts = start_ts + (h * 3600)
                
                # Linear interpolation formula: y = y0 + (x - x0) * (y1 - y0) / (x1 - x0)
                linear_val = start_val + (h / total_hours) * (end_val - start_val)
                
                # Tambahkan noise (Gaussian)
                noise = np.random.normal(0, self.noise_std) if self.noise_std > 0 else 0
                final_val = max(0, linear_val + noise) # APY/TVL tidak boleh negatif
                
                hourly_results.append({
                    "timestamp": current_ts,
                    field_name: final_val
                })
        
        # Tambahkan titik terakhir
        last_point = data_sorted[-1]
        hourly_results.append({
            "timestamp": last_point["timestamp"],
            field_name: last_point[field_name]
        })
        
        return hourly_results
