# aquashift.py - Live demo: run an ML job, measure it, convert to water, compare 11 regions.
#
# Usage:
#   py aquashift.py              # 200-tree Random Forest (the job in the paper)
#   py aquashift.py --trees 50   # a smaller model
#   py aquashift.py --scale 1000000   # also show the total for 1 million runs (linear)
#
# Energy is an ESTIMATE (45 W TDP, 5 W idle, linear in CPU utilisation), see aquameter.py.
# Water factors: Ren et al., arXiv:2304.03271, Table 1. Water stress: WRI Aqueduct 4.0.

import argparse
import sys

from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from aquameter import IDLE_W, TDP_W, measure
from stress import STRESS
from water2 import REGIONS, water_for

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BAR = "█"
CYAN, GREY, BOLD, RESET = "\033[36m", "\033[90m", "\033[1m", "\033[0m"
STRESS_SHORT = ["Low", "Low-Med", "Med-High", "High", "Extreme"]


def fmt_ml(ml):
    if ml >= 1_000_000:
        return f"{ml / 1_000_000:,.1f} m³"
    if ml >= 1000:
        return f"{ml / 1000:,.1f} L"
    return f"{ml:.3f} mL"


def main():
    p = argparse.ArgumentParser(description="AquaShift live demo")
    p.add_argument("--trees", type=int, default=200, help="number of trees (default 200)")
    p.add_argument("--scale", type=int, default=0,
                   help="also show the total water for this many runs (linear scaling)")
    args = p.parse_args()

    print(f"\n{BOLD}AquaShift{RESET} - water footprint of a compute job\n")
    print(f"Job: RandomForestClassifier, {args.trees} trees, 20,000 synthetic samples")

    X, y = make_classification(n_samples=20000, n_features=20, n_informative=10,
                               random_state=42)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

    def job():
        m = RandomForestClassifier(n_estimators=args.trees, n_jobs=-1, random_state=42)
        m.fit(X_tr, y_tr)
        return m.score(X_te, y_te)

    print("Training ... ", end="", flush=True)
    m = measure(job)
    print("done.\n")

    print(f"  Time          {m['duration_s']:.2f} s")
    print(f"  CPU use       {m['util_pct']:.1f} %")
    print(f"  Power         {m['power_w']:.1f} W   {GREY}(estimate: {IDLE_W} W idle .. "
          f"{TDP_W} W TDP){RESET}")
    print(f"  Energy        {m['energy_kwh']:.2e} kWh")
    print(f"  Accuracy      {m['result']:.4f}\n")

    rows = []
    for region in REGIONS:
        on, off, tot = water_for(region, m["energy_kwh"])
        score, _, _ = STRESS[region]
        rows.append((region, on * 1000, off * 1000, tot * 1000, score))
    rows.sort(key=lambda r: r[3])
    top = rows[-1][3]

    print(f"{BOLD}{'Region':12} {'Water':>10}  {'':24} {'On-site':>8}  "
          f"{'Water stress (0-5)':18}{RESET}")
    for region, on, off, tot, score in rows:
        n = max(1, round(24 * tot / top))
        bar = CYAN + BAR * n + RESET + " " * (24 - n)
        cls = STRESS_SHORT[min(int(score), 4)]
        print(f"{region:12} {tot:7.3f} mL  {bar} {100 * on / tot:6.1f} %  "
              f"{score:4.2f} {cls}")

    lo, hi = rows[0], rows[-1]
    print(f"\n{BOLD}Same job, {hi[3] / lo[3]:.1f}x more water{RESET} in {hi[0]} than in {lo[0]}.")
    min_on = min(100 * r[1] / r[3] for r in rows)
    max_on = max(100 * r[1] / r[3] for r in rows)
    print(f"On-site cooling is only {min_on:.0f}-{max_on:.0f} % of the total: "
          f"the electricity grid dominates.")
    low_l_high_s = [r[0] for r in rows[:4] if r[4] >= 3]
    if low_l_high_s:
        print(f"Careful: {', '.join(low_l_high_s)} use little water but have High water stress.")

    if args.scale:
        print(f"\n{BOLD}If this job ran {args.scale:,} times{RESET} {GREY}(linear scaling){RESET}:")
        for region, _, _, tot, _ in (rows[0], rows[len(rows) // 2], rows[-1]):
            print(f"  {region:12} {fmt_ml(tot * args.scale)}")

    print(f"\n{GREY}Estimates for comparison, not a measurement of any real facility.{RESET}\n")


if __name__ == "__main__":
    main()
