# background_video.py - Arka plan videoları (1920 x 1080, 30 fps, MP4)
#
# Kullanım:
#   py -m pip install imageio-ffmpeg     (ffmpeg'i kendi içinde getirir)
#   py background_video.py
# Çıktı (figures/video/):
#   background_loop.mp4   12 s, başa dönünce atlamayan döngü; yazı yok
#   logo_intro.mp4         6 s, aynı arka plan üstünde logo ve slogan belirir
#
# Tüm hareketler 12 saniyelik periyoda bağlı, bu yüzden döngü kesintisiz.

import math
import os
import random
import subprocess

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 1080, 30
LOOP_S = 12
TOP, BOTTOM = (11, 42, 54), (6, 24, 32)          # #0B2A36 -> #061820
ACCENT = (79, 200, 227)                            # #4FC8E3
LIGHT = (242, 247, 248)
OUT = "figures/video"
os.makedirs(OUT, exist_ok=True)

rng = random.Random(7)                             # same video on every run
TAU = 2 * math.pi

# --- static background: vertical gradient
g = np.linspace(0, 1, H)[:, None, None]
base = (np.array(TOP) + (np.array(BOTTOM) - np.array(TOP)) * g) * np.ones((1, W, 1))
BASE = Image.fromarray(base.astype(np.uint8), "RGB").convert("RGBA")

# --- drops: fall one or two screen heights per loop, sway sideways
DROPS = []
for _ in range(22):
    far = rng.random()                             # 0 = far (small, faint, blurry)
    DROPS.append({
        "x": rng.uniform(0, W), "y0": rng.uniform(0, H + 200),
        "r": 6 + 22 * far, "alpha": int(40 + 110 * far),
        "laps": 1 if far < 0.6 else 2,             # whole laps per loop -> seamless
        "sway": rng.uniform(8, 30), "phase": rng.uniform(0, TAU),
        "layer": 0 if far < 0.5 else 1,
    })

# --- flowing data lines: sine waves whose phase turns once per loop
LINES = [{"y": H * f, "amp": rng.uniform(14, 34), "k": rng.choice([2, 3]),
          "phase": rng.uniform(0, TAU), "alpha": rng.randint(18, 40)}
         for f in (0.24, 0.38, 0.62, 0.78)]

# --- ripples: each expands and fades once per loop, at its own start time
RIPPLES = [{"x": rng.uniform(200, W - 200), "y": rng.uniform(250, H - 150),
            "t0": i / 4} for i in range(4)]


def drop_poly(cx, cy, r, n=28):
    """Points of a water drop: round bottom of radius r, point 1.9 r above the centre."""
    # image y grows downwards: the round part is below the centre, the tip above it
    pts = [(cx + r * math.cos(math.pi * i / n), cy + r * math.sin(math.pi * i / n))
           for i in range(n + 1)]                  # bottom half circle, right to left
    pts += [(cx - 0.62 * r, cy - 0.85 * r), (cx, cy - 1.9 * r), (cx + 0.62 * r, cy - 0.85 * r)]
    return pts


def frame(t):
    """Render the background at time t (seconds); periodic with LOOP_S."""
    p = (t % LOOP_S) / LOOP_S                      # 0..1 over one loop
    img = BASE.copy()

    # slow glow circling the frame
    glow = Image.new("RGBA", (W // 4, H // 4), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gx = W // 8 + int(140 * math.cos(TAU * p))
    gy = H // 8 + int(70 * math.sin(TAU * p))
    for rad, a in ((170, 10), (120, 14), (80, 18)):
        gd.ellipse((gx - rad, gy - rad, gx + rad, gy + rad), fill=ACCENT + (a,))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)).resize((W, H)))

    # data lines
    lines = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lines)
    for ln in LINES:
        pts = [(x, ln["y"] + ln["amp"] * math.sin(TAU * (ln["k"] * x / W) + ln["phase"]
                                                  + TAU * p))
               for x in range(0, W + 1, 16)]
        ld.line(pts, fill=ACCENT + (ln["alpha"],), width=2)
    img.alpha_composite(lines)

    # ripples
    rip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rip)
    for r in RIPPLES:
        q = (p - r["t0"]) % 1.0
        if q < 0.5:                                # visible for half a loop
            s = q / 0.5
            for k, scale in enumerate((1.0, 0.65)):
                rad = (40 + 260 * s) * scale
                a = int(70 * (1 - s) * (1 - 0.4 * k))
                rd.ellipse((r["x"] - rad, r["y"] - rad * 0.35, r["x"] + rad, r["y"] + rad * 0.35),
                           outline=ACCENT + (a,), width=2)
    img.alpha_composite(rip)

    # drops: far layer blurred more than near layer
    for layer, blur in ((0, 6), (1, 2)):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        for d in DROPS:
            if d["layer"] != layer:
                continue
            span = H + 260
            y = (d["y0"] + span * d["laps"] * p) % span - 130
            x = d["x"] + d["sway"] * math.sin(TAU * p + d["phase"])
            dd.polygon(drop_poly(x, y, d["r"]), fill=ACCENT + (d["alpha"],))
        img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(blur)))
    return img


def encode(path, frames):
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium",
           "-movflags", "+faststart", path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for im in frames:
        proc.stdin.write(im.convert("RGB").tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg failed")
    print(path)


# --- 1. seamless loop
encode(f"{OUT}/background_loop.mp4", (frame(i / FPS) for i in range(LOOP_S * FPS)))

# --- 2. logo intro: mark and wordmark fade in over the same background
icon = Image.open("figures/logo/logo_icon_transparent.png").convert("RGBA")
icon = icon.crop(icon.getbbox()).resize((170, int(170 * icon.height / icon.width)))
bold = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 150)
tag = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 42)
word = Image.new("RGBA", (1300, 340), (0, 0, 0, 0))
wd = ImageDraw.Draw(word)
wd.text((0, 20), "WattToWater", font=bold, fill=LIGHT)
wd.text((6, 230), "A WATER METER FOR CODE", font=tag, fill=ACCENT)
word = word.crop(word.getbbox())
GAP = 60
total_w = icon.width + GAP + word.width
x0 = (W - total_w) // 2
ICON_POS = (x0, (H - icon.height) // 2)
WORD_POS = (x0 + icon.width + GAP, (H - word.height) // 2)


def fade(t, start, dur=0.8):
    s = min(max((t - start) / dur, 0), 1)
    return s * s * (3 - 2 * s)                     # smoothstep


def with_alpha(im, a):
    out = im.copy()
    out.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    return out


# soft dark halo behind the logo so it stays readable over drops and ripples
HALO = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(HALO).ellipse((x0 - 160, H // 2 - 230, x0 + total_w + 160, H // 2 + 230),
                             fill=BOTTOM + (170,))
HALO = HALO.filter(ImageFilter.GaussianBlur(90))


def intro(i):
    t = i / FPS
    img = frame(t)
    img.alpha_composite(with_alpha(HALO, fade(t, 0.0, 0.6)))
    a_icon, a_word = fade(t, 0.4), fade(t, 1.0)
    if a_icon:
        dy = int(20 * (1 - a_icon))
        img.alpha_composite(with_alpha(icon, a_icon), (ICON_POS[0], ICON_POS[1] + dy))
    if a_word:
        img.alpha_composite(with_alpha(word, a_word), WORD_POS)
    return img


encode(f"{OUT}/logo_intro.mp4", (intro(i) for i in range(6 * FPS)))
