# analysis.py - Makaledeki TÜM sayıları ve şekilleri tek komutla üretir.
#
# Kullanım:
#   py analysis.py
#
# Girdi : results.csv (Set 1, 3, 4), tradeoff.csv, water2.py (Ren ve ark. Tablo 1),
#         stress.py (WRI Aqueduct 4.0)
# Çıktı : outputs/*.csv  (makaledeki tablolar)
#         figures/*.png  (makaledeki şekiller)
# Yeni ölçüm yapmaz; sadece kayıtlı ölçümleri okur.

import csv
import os
import statistics

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from stress import STRESS  # noqa: E402
from water2 import REGIONS, water_for  # noqa: E402

N_RUNS_PER_SET = 5
SELECTED_SETS = [1, 3, 4]   # Set 2 aykırı, gerekçe: makale Bölüm 2.3

os.makedirs("outputs", exist_ok=True)
os.makedirs("figures", exist_ok=True)

# Renkler: tek mavi ton (büyüklük) + su stresi için tek sıcak ton rampası (açık -> koyu)
INK = "#14262d"
MUTED = "#6b7e85"
GRID = "#e3eaec"
BLUE = "#2f8fae"
BLUE_LIGHT = "#9fd0e0"
STRESS_RAMP = ["#f3d9a4", "#e9b44c", "#d9822b", "#b8501c", "#7f2410"]  # Low ... Extremely High
STRESS_NAMES = ["Low", "Low-Medium", "Medium-High", "High", "Extremely High"]

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "text.color": INK,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK,
    "ytick.color": INK, "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
})


def stress_class(score):
    """Aqueduct 0-5 puanını 0-4 kategori indeksine çevirir (1 puan = 1 sınıf)."""
    return min(int(score), 4)


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


# ---------------------------------------------------------------- 1. Enerji
with open("results.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))
selected = []
for s in SELECTED_SETS:
    selected += rows[(s - 1) * N_RUNS_PER_SET: s * N_RUNS_PER_SET]
energies = [float(r["energy_kwh"]) for r in selected]
e_mean, e_sd = statistics.mean(energies), statistics.stdev(energies)

print("SET ÖZETİ (results.csv)")
for s in range(1, len(rows) // N_RUNS_PER_SET + 1):
    part = rows[(s - 1) * N_RUNS_PER_SET: s * N_RUNS_PER_SET]
    d = [float(r["duration_s"]) for r in part]
    u = [float(r["util_pct"]) for r in part]
    used = "evet" if s in SELECTED_SETS else "HAYIR"
    print(f"  Set {s}: {part[0]['condition']:24} süre {statistics.mean(d):.2f} ± "
          f"{statistics.stdev(d):.2f} s, kullanım %{statistics.mean(u):.1f}, kullanıldı: {used}")
print(f"\nEnerji ({len(energies)} çalıştırma): {e_mean:.3e} ± {e_sd:.1e} kWh\n")

# ------------------------------------------------- 2. Bölge faktörleri (L/kWh)
factor_rows = []
for region, (pue, wue, ewif) in REGIONS.items():
    onsite, offsite, total = water_for(region, 1.0)
    factor_rows.append([region, pue, wue, ewif, round(onsite, 3), round(offsite, 3),
                        round(total, 3), round(100 * onsite / total, 1)])
factor_rows.sort(key=lambda r: r[6])
write_csv("outputs/table_factors.csv",
          ["region", "PUE", "WUE_L_per_kWh", "EWIF_L_per_kWh", "onsite_L_per_kWh",
           "offsite_L_per_kWh", "total_L_per_kWh", "onsite_share_pct"], factor_rows)

print("BÖLGE FAKTÖRLERİ (L/kWh)")
for r in factor_rows:
    print(f"  {r[0]:12} toplam {r[6]:6.3f}  tesis içi payı %{r[7]:4.1f}")
spread = factor_rows[-1][6] / factor_rows[0][6]
print(f"  En yüksek / en düşük: {spread:.1f} kat\n")

# ---------------------------------------- 3. Ana tablo: su + su stresi (mL)
main_rows = []
for region in REGIONS:
    waters = [water_for(region, e)[2] * 1000 for e in energies]
    score, label, level = STRESS[region]
    main_rows.append([region, round(statistics.mean(waters), 3), round(statistics.stdev(waters), 3),
                      round(score, 2), label, "country" if level == "ülke" else "state"])
main_rows.sort(key=lambda r: r[1])
write_csv("outputs/table_water_stress.csv",
          ["region", "water_ml_mean", "water_ml_sd", "bws_score_0_5", "bws_category", "level"],
          main_rows)

print("SU VE SU STRESİ (Random Forest, 200 ağaç)")
for r in main_rows:
    print(f"  {r[0]:12} {r[1]:.3f} ± {r[2]:.3f} mL   stres {r[3]:.2f}  {r[4]}")
print()

# ------------------------------------------------ 4. Model boyutu (tradeoff)
with open("tradeoff.csv", encoding="utf-8-sig") as f:
    trows = list(csv.DictReader(f))
trees_list = sorted({int(r["trees"]) for r in trows})
trade = []
for t in trees_list:
    part = [r for r in trows if int(r["trees"]) == t]
    e = [float(r["energy_kwh"]) for r in part]
    a = [float(r["accuracy"]) for r in part]
    d = [float(r["duration_s"]) for r in part]
    trade.append([t, len(part), statistics.mean(a), statistics.mean(d), statistics.mean(e),
                  statistics.stdev(e)])
ref_e = trade[-1][4]
trade_out = []
print("MODEL BOYUTU (tradeoff.csv)")
for t, n, a, d, e, sd in trade:
    trade_out.append([t, n, round(a, 4), round(d, 3), f"{e:.3e}", f"{sd:.1e}",
                      round(100 * e / ref_e, 1)])
    print(f"  {t:3d} ağaç: doğruluk {a:.4f}, süre {d:.2f} s, enerji {e:.3e} kWh "
          f"(%{100 * e / ref_e:.0f})")
write_csv("outputs/table_tradeoff.csv",
          ["trees", "runs", "accuracy", "duration_s_mean", "energy_kwh_mean", "energy_kwh_sd",
           "energy_pct_of_200"], trade_out)
print()

# ================================================================ ŞEKİLLER
# Şekil 1: bölge başına su (mL), tesis içi / tesis dışı ayrımı
fig, ax = plt.subplots(figsize=(7.2, 4.2))
names = [r[0] for r in factor_rows]
on = [r[4] * e_mean * 1000 for r in factor_rows]
off = [r[5] * e_mean * 1000 for r in factor_rows]
y = range(len(names))
ax.barh(y, off, color=BLUE, height=0.62, label="Off-site (electricity generation)")
ax.barh(y, on, left=off, color=BLUE_LIGHT, height=0.62, label="On-site (cooling)",
        edgecolor="white", linewidth=1)
for i, (a, b) in enumerate(zip(on, off)):
    ax.text(a + b + 0.008, i, f"{a + b:.3f}", va="center", fontsize=9, color=INK)
ax.set_yticks(list(y), names)
ax.set_xlabel("Water footprint of one training run (mL)")
ax.xaxis.grid(True, color=GRID)
ax.set_axisbelow(True)
ax.set_xlim(0, max(o + f for o, f in zip(on, off)) * 1.15)
ax.legend(frameon=False, loc="lower right")
ax.set_title("Same job, 11 regions: 6.7x difference in water", loc="left", fontsize=11,
             fontweight="bold")
fig.savefig("figures/fig1_water_by_region.png")
plt.close(fig)

# Şekil 2: litre ve su stresi (dağılım grafiği)
fig, ax = plt.subplots(figsize=(7.2, 4.6))
for r in main_rows:
    region, w, sd, score = r[0], r[1], r[2], r[3]
    c = STRESS_RAMP[stress_class(score)]
    ax.errorbar(w, score, xerr=sd, fmt="none", ecolor=MUTED, elinewidth=1, capsize=2, zorder=1)
    ax.scatter(w, score, s=90, color=c, edgecolor=INK, linewidth=0.6, zorder=2)
    # Etiket konumu (nokta cinsinden kaydırma): varsayılan noktanın üstü
    offsets = {"Virginia": (-4, 10, "center", "bottom"), "Illinois": (0, -12, "center", "top"),
               "US average": (8, 8, "left", "bottom"), "Iowa": (0, -14, "center", "top"),
               "Ireland": (10, 0, "left", "center"), "Texas": (10, 0, "left", "center"),
               "Wyoming": (10, 0, "left", "center"), "Netherlands": (10, 4, "left", "bottom")}
    ox, oy, ha, va = offsets.get(region, (0, 10, "center", "bottom"))
    ax.annotate(region, (w, score), xytext=(ox, oy), textcoords="offset points",
                fontsize=9, ha=ha, va=va)
for k in range(1, 5):
    ax.axhline(k, color=GRID, linewidth=1, zorder=0)
for k, n in enumerate(STRESS_NAMES):
    ax.text(0.006, k + 0.5, n, fontsize=8, color=MUTED, va="center", ha="left")
ax.set_xlim(0, 0.79)
ax.set_ylim(0, 5)
ax.set_xlabel("Water footprint of one training run (mL)")
ax.set_ylabel("WRI Aqueduct baseline water stress (0-5)")
ax.set_title("Litres and scarcity rank regions differently", loc="left", fontsize=11,
             fontweight="bold")
fig.savefig("figures/fig2_water_vs_stress.png")
plt.close(fig)

# Şekil 3: model boyutu - enerji payı ve doğruluk (iki ayrı panel, tek eksen kuralı)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.2))
tl = [str(r[0]) for r in trade]
ax1.bar(tl, [100 * r[4] / ref_e for r in trade], color=BLUE, width=0.6)
for i, r in enumerate(trade):
    ax1.text(i, 100 * r[4] / ref_e + 2, f"{100 * r[4] / ref_e:.0f}%", ha="center", fontsize=9)
ax1.set_ylim(0, 115)
ax1.set_xlabel("Number of trees")
ax1.set_ylabel("Energy and water (% of 200 trees)")
ax1.yaxis.grid(True, color=GRID)
ax1.set_axisbelow(True)
ax2.plot(tl, [100 * r[2] for r in trade], color=BLUE, linewidth=2, marker="o", markersize=7)
for i, r in enumerate(trade):
    below = i == 0
    ax2.text(i, 100 * r[2] + (-0.09 if below else 0.06), f"{100 * r[2]:.2f}", ha="center",
             va="top" if below else "bottom", fontsize=9)
ax2.set_ylim(94.5, 96.5)
ax2.set_xlabel("Number of trees")
ax2.set_ylabel("Test accuracy (%)")
ax2.yaxis.grid(True, color=GRID)
ax2.set_axisbelow(True)
fig.suptitle("Fewer trees: much less water, almost the same accuracy", x=0.02, ha="left",
             fontsize=11, fontweight="bold")
fig.tight_layout()
fig.savefig("figures/fig3_model_size.png")
plt.close(fig)

print("Tablolar: outputs/  |  Şekiller: figures/")
