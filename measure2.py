# measure2.py - İşlemci kullanımına göre enerji tahmini (Adım 4)

import time

import psutil

from water2 import REGIONS, water_for

# VARSAYIMLAR (ölçüm değil):
TDP_W = 45    # i5-12450H nominal gücü, tam yük (Intel teknik özellikleri)
IDLE_W = 5    # boşta güç: bizim kabulümüz, kaynağı yok
# Model: güç = IDLE_W + (TDP_W - IDLE_W) x kullanım oranı (doğrusal, kaba yaklaşım)

CHUNK_S = 0.5     # her 0,5 saniyede bir kullanım okuyoruz
CHUNKS = 20       # toplam 10 saniye


def busy_chunk(seconds):
    """İşlemciyi meşgul eden basit bir iş (tek çekirdek)."""
    end = time.perf_counter() + seconds
    while time.perf_counter() < end:
        sum(i * i for i in range(10000))


def power_w(utilization_pct):
    return IDLE_W + (TDP_W - IDLE_W) * utilization_pct / 100


psutil.cpu_percent(None)          # ilk çağrı anlamsız bir değer verir, atıyoruz
energy_joule = 0.0
util_list = []
t0 = time.perf_counter()

for _ in range(CHUNKS):
    busy_chunk(CHUNK_S)
    util = psutil.cpu_percent(None)   # son çağrıdan bu yana ortalama kullanım (%)
    util_list.append(util)
    energy_joule += power_w(util) * CHUNK_S   # J = W x s

duration_s = time.perf_counter() - t0
energy_kwh = energy_joule / 3_600_000         # 1 kWh = 3 600 000 J
avg_util = sum(util_list) / len(util_list)

print(f"Süre            : {duration_s:.2f} s")
print(f"Ortalama kullanım: %{avg_util:.1f}")
print(f"Ortalama güç    : {energy_joule / (CHUNK_S * CHUNKS):.1f} W (tahmin)")
print(f"Enerji          : {energy_kwh:.6f} kWh (tahmin)")
print()
for region in REGIONS:
    onsite, offsite, total = water_for(region, energy_kwh)
    print(f"{region:12} toplam: {total * 1000:.3f} mL")
