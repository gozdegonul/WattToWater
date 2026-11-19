# icons.py - "How it works" adımları için 4 ikon (512 x 512 PNG, banner ile aynı renkler)
#
# Kullanım:
#   py icons.py
# Çıktı: figures/icons/step1_measure.png ... step4_decide.png

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import (Circle, FancyBboxPatch, PathPatch,  # noqa: E402
                                Polygon, Rectangle)
from matplotlib.path import Path  # noqa: E402

TILE, EDGE = "#0f3542", "#1d4b5a"
ACCENT, SOFT, INK = "#4fc8e3", "#2b6f86", "#f2f8fa"
LW = 14          # line width of the icon strokes (points)

os.makedirs("figures/icons", exist_ok=True)


def canvas():
    fig = plt.figure(figsize=(5.12, 5.12), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((4, 4), 92, 92, boxstyle="round,pad=0,rounding_size=20",
                                facecolor=TILE, edgecolor=EDGE, linewidth=4))
    return fig, ax


def save(fig, name):
    fig.savefig(f"figures/icons/{name}.png", transparent=True)
    plt.close(fig)
    print(f"figures/icons/{name}.png")


def line(ax, xs, ys, color=ACCENT, lw=LW):
    ax.plot(xs, ys, color=color, linewidth=lw, solid_capstyle="round",
            solid_joinstyle="round")


def drop(cx, cy, r):
    """Water-drop path: round bottom of radius r, point at the top."""
    k = 0.5523 * r
    verts = [(cx, cy + 2.1 * r),                                  # tip
             (cx + 0.35 * r, cy + 1.4 * r), (cx + r, cy + 0.75 * r), (cx + r, cy),
             (cx + r, cy - k), (cx + k, cy - r), (cx, cy - r),
             (cx - k, cy - r), (cx - r, cy - k), (cx - r, cy),
             (cx - r, cy + 0.75 * r), (cx - 0.35 * r, cy + 1.4 * r), (cx, cy + 2.1 * r),
             (cx, cy + 2.1 * r)]
    codes = ([Path.MOVETO] + [Path.CURVE4] * 12 + [Path.CLOSEPOLY])
    return Path(verts, codes)


# 1. Measure: stopwatch
fig, ax = canvas()
ax.add_patch(Circle((50, 45), 26, fill=False, edgecolor=ACCENT, linewidth=LW))
line(ax, [50, 50], [71, 78])                                  # stem
line(ax, [43, 57], [80, 80])                                  # button
line(ax, [70, 76], [65, 71], color=SOFT)                      # side button
for a in np.radians([90, 0, 180, 270]):                       # ticks
    line(ax, [50 + 18 * np.cos(a), 50 + 22 * np.cos(a)],
         [45 + 18 * np.sin(a), 45 + 22 * np.sin(a)], color=SOFT, lw=8)
a = np.radians(55)
line(ax, [50, 50 + 15 * np.cos(a)], [45, 45 + 15 * np.sin(a)])   # needle
ax.add_patch(Circle((50, 45), 3.5, color=ACCENT))
save(fig, "step1_measure")

# 2. Convert: lightning bolt -> water drop
fig, ax = canvas()
bolt = [(30, 76), (17, 48), (28, 48), (22, 24), (40, 54), (29, 54), (37, 76)]
ax.add_patch(Polygon(bolt, closed=True, facecolor=SOFT, edgecolor=SOFT, linewidth=4,
                     joinstyle="round"))
line(ax, [45, 58], [50, 50], color=INK, lw=9)                 # arrow shaft
line(ax, [53, 59, 53], [56, 50, 44], color=INK, lw=9)         # arrow head
ax.add_patch(PathPatch(drop(75, 40, 13), facecolor=ACCENT, edgecolor=ACCENT, linewidth=2))
save(fig, "step2_convert")

# 3. Report: document with a bar chart
fig, ax = canvas()
doc = [(28, 22), (28, 80), (60, 80), (72, 68), (72, 22)]
ax.add_patch(Polygon(doc, closed=True, fill=False, edgecolor=ACCENT, linewidth=LW,
                     joinstyle="round"))
line(ax, [60, 60, 72], [80, 68, 68], lw=8)                    # folded corner
for x, h in [(37, 14), (48, 26), (59, 19)]:
    ax.add_patch(Rectangle((x - 3.5, 31), 7, h, facecolor=SOFT if h != 26 else ACCENT,
                           edgecolor="none"))
line(ax, [35, 52], [66, 66], color=SOFT, lw=7)                # title line
save(fig, "step3_report")

# 4. Decide: signpost with two directions
fig, ax = canvas()
line(ax, [50, 50], [18, 82], color=SOFT)                      # pole
right = [(50, 70), (74, 70), (82, 62), (74, 54), (50, 54)]
left = [(50, 46), (26, 46), (18, 38), (26, 30), (50, 30)]
ax.add_patch(Polygon(right, closed=True, facecolor=ACCENT, edgecolor=ACCENT, linewidth=4,
                     joinstyle="round"))
ax.add_patch(Polygon(left, closed=True, facecolor="none", edgecolor=ACCENT, linewidth=8,
                     joinstyle="round"))
line(ax, [58, 63, 71], [62, 57, 66], color=TILE, lw=7)        # check mark on the chosen way
save(fig, "step4_decide")
