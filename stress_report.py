# stress_report.py - Su ve su stresini yan yana raporla (Adım 8)
#
# results.csv'deki ölçümleri okur, seçili setleri kullanır,
# bölge başına: su (mL), su stresi puanı ve (ikincil) stres ağırlıklı su.

import csv
import statistics

from stress import STRESS
from water2 import REGIONS, water_for

N_RUNS_PER_SET = 5

# Kullandığımız setler (results.csv'de 5'erli gruplar, sırayla):
#   1 = tüm uygulamalar kapalı, 2 = geliştirme araçları açık (AYKIRI),
#   3 = geliştirme araçları açık, 4 = tüm uygulamalar kapalı
# Set 2 çıkarıldı: aynı koşul (set 3) çok farklı sonuç verdi, olası sebep
# uygulama açılışı sonrası arka plan yükü (kanıtlanmadı). Dosyada duruyor.
SELECTED_SETS = [1, 3, 4]

with open("results.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

selected = []
for s in SELECTED_SETS:
    start = (s - 1) * N_RUNS_PER_SET
    selected += rows[start:start + N_RUNS_PER_SET]

energies = [float(r["energy_kwh"]) for r in selected]
print(f"Kullanılan ölçüm sayısı: {len(selected)} (setler {SELECTED_SETS})")
print(f"Enerji: {statistics.mean(energies):.7f} ± {statistics.stdev(energies):.7f} kWh (tahmin)")
print()
print(f"{'Bölge':12} {'Su (mL)':>16}  {'Stres':>5}  {'Kategori':22} {'Düzey':7} {'Stres ağırlıklı*':>16}")

for region in REGIONS:
    waters_ml = [water_for(region, e)[2] * 1000 for e in energies]
    w_mean = statistics.mean(waters_ml)
    w_std = statistics.stdev(waters_ml)
    score, label, level = STRESS[region]
    weighted = w_mean * score / 5
    print(f"{region:12} {w_mean:7.3f} ± {w_std:5.3f}  {score:5.2f}  {label:22} {level:7} {weighted:16.3f}")

print()
print("* Stres ağırlıklı = su x (puan / 5). İkincil analiz: bu çarpımın")
print("  bilimsel dayanağı zayıf, sadece büyüklük sırası için bak.")
