# log_runs.py - İşi birkaç kez ölç ve her ölçümü results.csv dosyasına ekle (Adım 7)
#
# Kullanım:
#   py log_runs.py "arka plan uygulamaları kapalı"
# Tırnak içindeki yazı, ölçüm koşulunu açıklayan nottur.

import csv
import os
import sys
from datetime import datetime

from aquameter import IDLE_W, TDP_W, measure
from ml_job import job
from water2 import REGIONS, water_for

N_RUNS = 5
CSV_FILE = "results.csv"

condition = sys.argv[1] if len(sys.argv) > 1 else "belirtilmedi"

columns = ["timestamp", "condition", "run", "duration_s", "util_pct",
           "power_w", "energy_kwh", "tdp_w", "idle_w"]
columns += [f"water_ml_{region}" for region in REGIONS]

new_file = not os.path.exists(CSV_FILE)

with open(CSV_FILE, "a", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    if new_file:
        writer.writerow(columns)

    for i in range(N_RUNS):
        m = measure(job)
        row = [
            datetime.now().isoformat(timespec="seconds"),
            condition,
            i + 1,
            round(m["duration_s"], 3),
            round(m["util_pct"], 1),
            round(m["power_w"], 2),
            f"{m['energy_kwh']:.9f}",
            TDP_W,
            IDLE_W,
        ]
        for region in REGIONS:
            total_l = water_for(region, m["energy_kwh"])[2]
            row.append(round(total_l * 1000, 4))
        writer.writerow(row)
        print(f"Çalıştırma {i + 1}/{N_RUNS} kaydedildi: "
              f"{m['duration_s']:.2f} s, %{m['util_pct']:.1f}")

print(f"\nSonuçlar {CSV_FILE} dosyasına eklendi. Koşul: {condition}")
