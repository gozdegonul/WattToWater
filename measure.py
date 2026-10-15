# measure.py - Bir işin süresini ölç, enerjiye ve suya çevir (Adım 3)

import time
from water2 import REGIONS, water_for

# VARSAYIM (ölçüm değil): i5-12450H nominal gücü (TDP) = 45 W, tam yük.
# Kaynak: Intel teknik özellikleri. Gerçek değer bundan düşük veya yüksek olabilir.
WATTS = 45


def busy_work(seconds):
    """İşlemciyi meşgul eden basit bir iş."""
    end = time.perf_counter() + seconds
    while time.perf_counter() < end:
        sum(i * i for i in range(10000))


start = time.perf_counter()
busy_work(10)
duration_s = time.perf_counter() - start

# Enerji (kWh) = Güç (W) x süre (s) / 3 600 000
energy_kwh = WATTS * duration_s / 3_600_000

print(f"Süre   : {duration_s:.2f} s")
print(f"Güç    : {WATTS} W (varsayım)")
print(f"Enerji : {energy_kwh:.6f} kWh")
print()
for region in REGIONS:
    onsite, offsite, total = water_for(region, energy_kwh)
    print(f"{region:12} toplam: {total * 1000:.3f} mL")
