# repeat_ml.py - Aynı işi birkaç kez ölç, ortalama ve sapmayı yaz (Adım 6)

import statistics

from aquameter import measure
from ml_job import job
from water2 import REGIONS, water_for

N_RUNS = 5

runs = []
for i in range(N_RUNS):
    m = measure(job)
    runs.append(m)
    print(f"Çalıştırma {i + 1}: {m['duration_s']:.2f} s, "
          f"kullanım %{m['util_pct']:.1f}, {m['energy_kwh']:.6f} kWh")


def mean_std(values):
    return statistics.mean(values), statistics.stdev(values)


print()
dur_mean, dur_std = mean_std([m["duration_s"] for m in runs])
en_mean, en_std = mean_std([m["energy_kwh"] for m in runs])
print(f"Süre   : {dur_mean:.2f} ± {dur_std:.2f} s")
print(f"Enerji : {en_mean:.6f} ± {en_std:.6f} kWh (tahmin)")
print()

for region in REGIONS:
    waters_ml = [water_for(region, m["energy_kwh"])[2] * 1000 for m in runs]
    w_mean, w_std = mean_std(waters_ml)
    print(f"{region:12} su: {w_mean:.3f} ± {w_std:.3f} mL")
