# tradeoff.py - Model boyutu: doğruluk, enerji ve su (Kol 2)
#
# Soru: Ağaç sayısını azaltırsak doğruluk ne kadar düşer, enerji ve su ne kadar azalır?
#
# Kullanım:
#   py tradeoff.py "tüm uygulamalar kapalı"

import csv
import os
import sys
import time
from datetime import datetime

from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from aquameter import IDLE_W, TDP_W, measure
from water2 import REGIONS, water_for

TREES = [25, 50, 100, 200]   # denenecek ağaç sayıları
REPEATS = 3                  # her ayar kaç kez ölçülecek
COOLDOWN_S = 10              # çalıştırmalar arası dinlenme (saniye)
CSV_FILE = "tradeoff.csv"

condition = sys.argv[1] if len(sys.argv) > 1 else "belirtilmedi"

# Aynı veri ve aynı bölme ml_job.py ile (random_state sabit)
X, y = make_classification(
    n_samples=20000, n_features=20, n_informative=10, random_state=42
)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

columns = ["timestamp", "condition", "trees", "rep", "duration_s", "util_pct",
           "power_w", "energy_kwh", "accuracy", "tdp_w", "idle_w"]
columns += [f"water_ml_{region}" for region in REGIONS]
new_file = not os.path.exists(CSV_FILE)

results = []   # (trees, accuracy, energy_kwh)

with open(CSV_FILE, "a", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    if new_file:
        writer.writerow(columns)

    for rep in range(REPEATS):
        # Sırayı her turda çeviriyoruz: ısınma etkisi bir ayara kayırmasın
        order = TREES if rep % 2 == 0 else list(reversed(TREES))
        for trees in order:
            def job(trees=trees):
                model = RandomForestClassifier(
                    n_estimators=trees, n_jobs=-1, random_state=42
                )
                model.fit(X_train, y_train)
                return model.score(X_test, y_test)

            m = measure(job)
            row = [
                datetime.now().isoformat(timespec="seconds"), condition, trees,
                rep + 1, round(m["duration_s"], 3), round(m["util_pct"], 1),
                round(m["power_w"], 2), f"{m['energy_kwh']:.9f}",
                round(m["result"], 4), TDP_W, IDLE_W,
            ]
            for region in REGIONS:
                row.append(round(water_for(region, m["energy_kwh"])[2] * 1000, 4))
            writer.writerow(row)
            f.flush()
            results.append((trees, m["result"], m["energy_kwh"]))
            print(f"tur {rep + 1}/{REPEATS}, {trees:3d} ağaç: "
                  f"doğruluk {m['result']:.3f}, {m['duration_s']:.2f} s, "
                  f"{m['energy_kwh']:.7f} kWh")
            time.sleep(COOLDOWN_S)

# Özet
print()
print(f"{'Ağaç':>5} {'Doğruluk':>9} {'Enerji (kWh)':>14} {'Enerji, 200 ağaca göre':>24}")
ref = [e for t, a, e in results if t == max(TREES)]
ref_mean = sum(ref) / len(ref)
for trees in TREES:
    accs = [a for t, a, e in results if t == trees]
    ens = [e for t, a, e in results if t == trees]
    e_mean = sum(ens) / len(ens)
    print(f"{trees:5d} {sum(accs) / len(accs):9.3f} {e_mean:14.7f} {100 * e_mean / ref_mean:23.0f}%")
print(f"\nSonuçlar {CSV_FILE} dosyasına eklendi. Koşul: {condition}")
