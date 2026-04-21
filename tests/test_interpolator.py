import pytest
import numpy as np
from defi_agent.backtest.interpolator import HourlyInterpolator

def test_interpolation_linear():
    # Simulasi data harian: 10% hari ke-0, 12% hari ke-1
    daily_data = [
        {"timestamp": 0, "apy": 10.0},
        {"timestamp": 86400, "apy": 12.0} # 86400 detik = 1 hari
    ]
    
    # Tanpa noise untuk verifikasi linearitas
    interpolator = HourlyInterpolator(noise_std=0.0)
    hourly_data = interpolator.generate_hourly(daily_data, "apy")
    
    # Seharusnya ada 25 titik data (0, 1, ..., 24 jam)
    assert len(hourly_data) == 25
    
    # Titik tengah (jam ke-12) seharusnya 11.0% (rata-rata 10 dan 12)
    assert hourly_data[12]["apy"] == 11.0
    assert hourly_data[0]["apy"] == 10.0
    assert hourly_data[24]["apy"] == 12.0

def test_interpolation_with_noise():
    daily_data = [
        {"timestamp": 0, "apy": 10.0},
        {"timestamp": 86400, "apy": 10.0}
    ]
    
    # Pakai noise 0.5
    interpolator = HourlyInterpolator(noise_std=0.5)
    hourly_data = interpolator.generate_hourly(daily_data, "apy")
    
    # Nilai tidak boleh persis 10.0 di titik tengah
    assert hourly_data[12]["apy"] != 10.0
    # Tapi masih dalam rentang normal (misal 3 standar deviasi)
    assert 8.0 < hourly_data[12]["apy"] < 12.0
