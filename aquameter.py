# aquameter.py - Herhangi bir işi ölç: süre -> enerji -> su (Adım 5)

import time

import psutil

from water2 import REGIONS, water_for

# VARSAYIMLAR (ölçüm değil):
TDP_W = 45    # i5-12450H nominal gücü, tam yük (Intel teknik özellikleri)
IDLE_W = 5    # boşta güç: bizim kabulümüz, kaynağı yok
# Model: güç = IDLE_W + (TDP_W - IDLE_W) x kullanım oranı (doğrusal, kaba yaklaşım)


def measure(job):
    """job() fonksiyonunu çalıştırır, süresini ve ortalama işlemci kullanımını ölçer.

    Model doğrusal olduğu için ortalama kullanım, parça parça örneklemekle
    aynı enerjiyi verir. Bu yüzden başta ve sonda bir kez okumak yeterli.
    """
    psutil.cpu_percent(None)              # sayacı sıfırla (ilk değer anlamsız)
    t0 = time.perf_counter()
    result = job()
    duration_s = time.perf_counter() - t0
    util = psutil.cpu_percent(None)       # işin boyunca ortalama kullanım (%)

    power_w = IDLE_W + (TDP_W - IDLE_W) * util / 100
    energy_kwh = power_w * duration_s / 3_600_000
    return {
        "result": result,
        "duration_s": duration_s,
        "util_pct": util,
        "power_w": power_w,
        "energy_kwh": energy_kwh,
    }


def report(m):
    print(f"Süre             : {m['duration_s']:.2f} s")
    print(f"Ortalama kullanım: %{m['util_pct']:.1f}")
    print(f"Ortalama güç     : {m['power_w']:.1f} W (tahmin)")
    print(f"Enerji           : {m['energy_kwh']:.6f} kWh (tahmin)")
    print()
    for region in REGIONS:
        onsite, offsite, total = water_for(region, m["energy_kwh"])
        print(f"{region:12} toplam: {total * 1000:.3f} mL")
