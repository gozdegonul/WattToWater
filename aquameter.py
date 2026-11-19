# aquameter.py - Herhangi bir işi ölç: süre -> enerji -> su (Adım 5)

from watttowater.meter import IDLE_W, TDP_W, measure  # noqa: F401
from water2 import REGIONS, water_for

# VARSAYIMLAR ve ölçüm kodu artık tek kaynakta: watttowater/meter.py
#   güç = IDLE_W + (TDP_W - IDLE_W) x kullanım oranı (doğrusal, kaba yaklaşım)
#   TDP_W = 45 W (Intel, i5-12450H temel güç), IDLE_W = 5 W (bizim kabulümüz)


def report(m):
    print(f"Süre             : {m['duration_s']:.2f} s")
    print(f"Ortalama kullanım: %{m['util_pct']:.1f}")
    print(f"Ortalama güç     : {m['power_w']:.1f} W (tahmin)")
    print(f"Enerji           : {m['energy_kwh']:.6f} kWh (tahmin)")
    print()
    for region in REGIONS:
        onsite, offsite, total = water_for(region, m["energy_kwh"])
        print(f"{region:12} toplam: {total * 1000:.3f} mL")
