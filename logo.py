# logo.py - WattToWater logosu: içinde şimşek olan bir su damlası (watt -> water)
#
# Kullanım:
#   py logo.py
# Çıktı (figures/logo/):
#   logo_icon.png              1024 x 1024, koyu zemin (profil görseli; daire kırpmaya uygun)
#   logo_icon_transparent.png  1024 x 1024, saydam zemin
#   logo_horizontal.png        2400 x 800, ikon + yazı, koyu zemin
#   logo_horizontal_light.png  2400 x 800, ikon + yazı, açık zemin

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, PathPatch, Polygon  # noqa: E402
from matplotlib.path import Path  # noqa: E402

DEEP, DARK = "#071D26", "#0B2A36"
ACCENT, ACCENT_DARK = "#4FC8E3", "#2B9CB8"
INK_LIGHT, INK_DARK = "#F2F7F8", "#0B2A36"
PAPER = "#F6F8F7"
FONT = "Segoe UI"

os.makedirs("figures/logo", exist_ok=True)


def drop_path(cx, cy, r):
    """Water drop: round bottom of radius r centred at (cx, cy), point at the top."""
    k = 0.5523 * r
    top = cy + 2.05 * r
    verts = [(cx, top),
             (cx + 0.30 * r, top - 0.65 * r), (cx + r, cy + 0.80 * r), (cx + r, cy),
             (cx + r, cy - k), (cx + k, cy - r), (cx, cy - r),
             (cx - k, cy - r), (cx - r, cy - k), (cx - r, cy),
             (cx - r, cy + 0.80 * r), (cx - 0.30 * r, top - 0.65 * r), (cx, top),
             (cx, top)]
    codes = [Path.MOVETO] + [Path.CURVE4] * 12 + [Path.CLOSEPOLY]
    return Path(verts, codes)


def bolt(cx, cy, s):
    """Lightning bolt centred near (cx, cy), height about 2.2 * s."""
    pts = [(0.02, 1.05), (-0.52, -0.08), (-0.04, -0.08), (-0.30, -1.05),
           (0.54, 0.20), (0.06, 0.20), (0.44, 1.05)]
    return [(cx + x * s, cy + y * s) for x, y in pts]


def draw_mark(ax, cx, cy, r, bolt_color):
    """The mark: a drop with a lightning bolt cut out of it, plus a soft highlight."""
    ax.add_patch(PathPatch(drop_path(cx, cy, r), facecolor=ACCENT, edgecolor="none"))
    ax.add_patch(Polygon(bolt(cx - 0.02 * r, cy + 0.33 * r, 0.66 * r), closed=True,
                         facecolor=bolt_color, edgecolor=bolt_color, linewidth=0.5,
                         joinstyle="miter"))


def square(name, background):
    fig = plt.figure(figsize=(10.24, 10.24), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect("equal")
    ax.axis("off")
    if background:
        ax.add_patch(Circle((50, 50), 70.8, color=DARK))     # fills the square
        ax.add_patch(Circle((50, 50), 46, color="#0F3542"))   # soft disc inside the crop circle
    # the drop stays inside the central circle (radius 50) so a round crop keeps it whole
    draw_mark(ax, 50, 39.5, 20, DARK if background else DEEP)
    fig.savefig(f"figures/logo/{name}.png", transparent=not background)
    plt.close(fig)
    print(f"figures/logo/{name}.png")


def horizontal(name, bg, text_color, bolt_color):
    fig = plt.figure(figsize=(24, 8), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 300)
    ax.set_ylim(0, 100)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(bg)
    draw_mark(ax, 52, 36, 19, bolt_color)
    ax.text(92, 56, "WattToWater", color=text_color, fontsize=150, fontweight="bold",
            family=FONT, va="center")
    ax.text(94, 25, "A WATER METER FOR CODE", color=ACCENT_DARK if bg == PAPER else ACCENT,
            fontsize=44, fontweight="bold", family=FONT, va="center")
    fig.savefig(f"figures/logo/{name}.png", facecolor=bg)
    plt.close(fig)
    print(f"figures/logo/{name}.png")


square("logo_icon", background=True)
square("logo_icon_transparent", background=False)
horizontal("logo_horizontal", DARK, INK_LIGHT, DARK)
horizontal("logo_horizontal_light", PAPER, INK_DARK, PAPER)
