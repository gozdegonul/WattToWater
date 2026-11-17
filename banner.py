# banner.py - Proje banner'ı (1280 x 640, GitHub sosyal önizleme boyutu)
#
# Kullanım:
#   py banner.py
# Çıktı: figures/banner.png (2:1) ve figures/banner_wide.png (3:1, kapak görseli)
# Sayılar water2.py'den (Li ve ark., Tablo 1) ve makaledeki sonuçlardan gelir.

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

from water2 import REGIONS, water_for  # noqa: E402

BG_TOP, BG_BOTTOM = "#0b2a36", "#061820"
INK, INK2, MUTED = "#f2f8fa", "#b9d0d7", "#7f9aa3"
ACCENT, BAR, TILE = "#4fc8e3", "#2b6f86", "#0f3542"
FONT = "Segoe UI"

W, H = 12.8, 6.4
fig = plt.figure(figsize=(W, H), dpi=100)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")

# Arka plan: yukarıdan aşağı koyulaşan degrade
grad = np.linspace(0, 1, 256).reshape(-1, 1)
top = np.array(matplotlib.colors.to_rgb(BG_TOP))
bot = np.array(matplotlib.colors.to_rgb(BG_BOTTOM))
img = top + (bot - top) * grad[..., None]
ax.imshow(img, extent=(0, W, 0, H), aspect="auto", zorder=0)

# --- Sol: başlık ve slogan
x0 = 0.75
ax.text(x0, 5.55, "OPEN PROTOTYPE  ·  WATER FOOTPRINT OF COMPUTE", color=ACCENT,
        fontsize=11.5, fontweight="bold", family=FONT, va="center")
ax.text(x0 - 0.04, 4.72, "WattToWater", color=INK, fontsize=58, fontweight="bold",
        family=FONT, va="center")
ax.text(x0, 3.88, "How much water does your code use,", color=INK2, fontsize=19,
        family=FONT, va="center")
ax.text(x0, 3.46, "and where should it run?", color=INK2, fontsize=19, family=FONT,
        va="center")
ax.text(x0, 2.88, "W  =  E · WUE  +  E · PUE · EWIF", color=MUTED, fontsize=13,
        family="DejaVu Sans Mono", va="center")
ax.text(1.415, 2.6, "on-site cooling", color=MUTED, fontsize=8.5, family=FONT, va="center")
ax.text(2.725, 2.6, "off-site electricity generation", color=MUTED, fontsize=8.5, family=FONT,
        va="center")

# --- Alt: üç bulgu kutusu
tiles = [
    ("6.7×", "more water for the same job\nin the worst vs best region"),
    ("≥ 78%", "of the water comes from\ngenerating the electricity"),
    ("48%", "of the water with 100 trees\ninstead of 200, same accuracy"),
]
tw, th, gap, ty = 2.18, 1.28, 0.2, 0.62
for i, (big, small) in enumerate(tiles):
    tx = x0 + i * (tw + gap)
    ax.add_patch(FancyBboxPatch((tx, ty), tw, th, boxstyle="round,pad=0,rounding_size=0.14",
                                facecolor=TILE, edgecolor="#1d4b5a", linewidth=1, zorder=2))
    ax.text(tx + 0.2, ty + th - 0.36, big, color=ACCENT, fontsize=26, fontweight="bold",
            family=FONT, va="center", zorder=3)
    ax.text(tx + 0.2, ty + 0.36, small, color=INK2, fontsize=9.5, family=FONT,
            va="center", linespacing=1.35, zorder=3)

# --- Sağ: bölgelere göre su (L/kWh) çubukları
rows = sorted(((r, water_for(r, 1.0)[2]) for r in REGIONS), key=lambda t: t[1])
bx, bw_max = 9.05, 3.0
by0, step, bh = 0.78, 0.415, 0.25
ax.text(bx - 1.32, by0 + step * len(rows) + 0.12, "Litres of water per kWh, by region",
        color=INK2, fontsize=10.5, fontweight="bold", family=FONT, va="center")
top_val = rows[-1][1]
for i, (region, val) in enumerate(rows):
    y = by0 + i * step
    is_end = i in (0, len(rows) - 1)
    color = ACCENT if is_end else BAR
    ax.add_patch(FancyBboxPatch((bx, y), bw_max * val / top_val, bh,
                                boxstyle="round,pad=0,rounding_size=0.05",
                                facecolor=color, edgecolor="none", zorder=2))
    name = "U.S. avg." if region == "US average" else region
    ax.text(bx - 0.12, y + bh / 2, name, color=INK if is_end else INK2, fontsize=9.5,
            family=FONT, ha="right", va="center")
    ax.text(bx + bw_max * val / top_val + 0.08, y + bh / 2, f"{val:.1f}",
            color=INK if is_end else MUTED, fontsize=9, family=FONT, va="center",
            fontweight="bold" if is_end else "normal")

ax.text(W - 0.3, 0.22, "Regional factors: Li et al., arXiv:2304.03271, Table 1",
        color=MUTED, fontsize=7.5, family=FONT, ha="right", va="center")

fig.savefig("figures/banner.png", dpi=200)
print("figures/banner.png")


# =====================================================================
# Geniş sürüm: 3:1 (3000 x 1000), proje sayfası kapak görseli için.
# Platformlar kapak görselini ortadan kırpar; tüm içerik üst ve alttan
# en az %12 boşluk bırakan "güvenli alan" içinde durur.
W2, H2 = 15.0, 5.0
fig = plt.figure(figsize=(W2, H2), dpi=100)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W2)
ax.set_ylim(0, H2)
ax.axis("off")
ax.imshow(img, extent=(0, W2, 0, H2), aspect="auto", zorder=0)

# Sol: başlık
x0 = 0.75
ax.text(x0, 4.12, "OPEN PROTOTYPE  ·  WATER FOOTPRINT OF COMPUTE", color=ACCENT,
        fontsize=10.5, fontweight="bold", family=FONT, va="center")
ax.text(x0 - 0.04, 3.38, "WattToWater", color=INK, fontsize=52, fontweight="bold",
        family=FONT, va="center")
ax.text(x0, 2.58, "How much water does your code use,", color=INK2, fontsize=16,
        family=FONT, va="center")
ax.text(x0, 2.2, "and where should it run?", color=INK2, fontsize=16, family=FONT,
        va="center")
ax.text(x0, 1.45, "W  =  E · WUE  +  E · PUE · EWIF", color=MUTED, fontsize=12,
        family="DejaVu Sans Mono", va="center")
ax.text(x0 + 0.6, 1.17, "on-site cooling", color=MUTED, fontsize=8, family=FONT, va="center")
ax.text(x0 + 1.81, 1.17, "off-site electricity generation", color=MUTED, fontsize=8,
        family=FONT, va="center")

# Orta: üç bulgu kutusu, alt alta
tx, tw, th, tgap = 6.35, 3.15, 1.0, 0.18
ty_top = 4.3
for i, (big, small) in enumerate(tiles):
    ty = ty_top - th - i * (th + tgap)
    ax.add_patch(FancyBboxPatch((tx, ty), tw, th, boxstyle="round,pad=0,rounding_size=0.12",
                                facecolor=TILE, edgecolor="#1d4b5a", linewidth=1, zorder=2))
    ax.text(tx + 0.18, ty + th / 2, big, color=ACCENT, fontsize=22, fontweight="bold",
            family=FONT, va="center", zorder=3)
    ax.text(tx + 1.35, ty + th / 2, small, color=INK2, fontsize=8.6, family=FONT,
            va="center", linespacing=1.3, zorder=3)

# Sağ: bölge çubukları
bx, bw_max = 11.15, 2.85
by0, step, bh = 0.72, 0.305, 0.19
ax.text(bx - 1.15, by0 + step * len(rows) + 0.06, "Litres of water per kWh, by region",
        color=INK2, fontsize=9.5, fontweight="bold", family=FONT, va="center")
for i, (region, val) in enumerate(rows):
    y = by0 + i * step
    is_end = i in (0, len(rows) - 1)
    color = ACCENT if is_end else BAR
    ax.add_patch(FancyBboxPatch((bx, y), bw_max * val / top_val, bh,
                                boxstyle="round,pad=0,rounding_size=0.04",
                                facecolor=color, edgecolor="none", zorder=2))
    name = "U.S. avg." if region == "US average" else region
    ax.text(bx - 0.1, y + bh / 2, name, color=INK if is_end else INK2, fontsize=8.5,
            family=FONT, ha="right", va="center")
    ax.text(bx + bw_max * val / top_val + 0.07, y + bh / 2, f"{val:.1f}",
            color=INK if is_end else MUTED, fontsize=8, family=FONT, va="center",
            fontweight="bold" if is_end else "normal")

fig.savefig("figures/banner_wide.png", dpi=200)
print("figures/banner_wide.png")
