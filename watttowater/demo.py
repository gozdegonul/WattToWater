"""Live demo: train an ML model, measure it, convert to water, compare 11 regions.

    python -m watttowater                       # 200-tree Random Forest (the job in the paper)
    python -m watttowater --trees 100           # a smaller model
    python -m watttowater --max-stress 2        # only recommend regions with stress <= 2
    python -m watttowater --scale 1000000       # also show the total for 1 million runs

Energy is an ESTIMATE (base power 45 W, idle 5 W, linear in CPU utilisation), see meter.py.
"""

from .data import REGIONS, STRESS, STRESS_SHORT, stress_class, water_for
from .meter import IDLE_W, TDP_W, measure

BAR = "█"
CYAN, GREY, BOLD, RESET = "\033[36m", "\033[90m", "\033[1m", "\033[0m"


def fmt_ml(ml):
    if ml >= 1_000_000:
        return f"{ml / 1_000_000:,.1f} m³"
    if ml >= 1000:
        return f"{ml / 1000:,.1f} L"
    return f"{ml:.3f} mL"


def make_job(trees):
    """The benchmark job of the paper: Random Forest on 20,000 synthetic samples."""
    from sklearn.datasets import make_classification
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    X, y = make_classification(n_samples=20000, n_features=20, n_informative=10,
                               random_state=42)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

    def job():
        m = RandomForestClassifier(n_estimators=trees, n_jobs=-1, random_state=42)
        m.fit(X_tr, y_tr)
        return m.score(X_te, y_te)

    return job


def run(trees=200, scale=0, max_stress=None):
    print(f"\n{BOLD}WattToWater{RESET} - water footprint of a compute job\n")
    print(f"Job: RandomForestClassifier, {trees} trees, 20,000 synthetic samples")
    job = make_job(trees)

    print("Training ... ", end="", flush=True)
    m = measure(job)
    print("done.\n")

    print(f"  Time          {m['duration_s']:.2f} s")
    print(f"  CPU use       {m['util_pct']:.1f} %")
    print(f"  Power         {m['power_w']:.1f} W   {GREY}(estimate: {IDLE_W:g} W idle .. "
          f"{TDP_W:g} W base power){RESET}")
    print(f"  Energy        {m['energy_kwh']:.2e} kWh")
    print(f"  Accuracy      {m['result']:.4f}\n")

    rows = []
    for region in REGIONS:
        on, off, tot = water_for(region, m["energy_kwh"])
        rows.append((region, on * 1000, off * 1000, tot * 1000, STRESS[region][0]))
    rows.sort(key=lambda r: r[3])
    top = rows[-1][3]

    print(f"{BOLD}{'Region':12} {'Water':>10}  {'':24} {'On-site':>8}  "
          f"{'Water stress (0-5)':18}{RESET}")
    for region, on, off, tot, score in rows:
        n = max(1, round(24 * tot / top))
        bar = CYAN + BAR * n + RESET + " " * (24 - n)
        over = max_stress is not None and score > max_stress
        flag = f"  {GREY}over limit{RESET}" if over else ""
        print(f"{region:12} {tot:7.3f} mL  {bar} {100 * on / tot:6.1f} %  "
              f"{score:4.2f} {STRESS_SHORT[stress_class(score)]}{flag}")

    lo, hi = rows[0], rows[-1]
    print(f"\n{BOLD}Same job, {hi[3] / lo[3]:.1f}x more water{RESET} in {hi[0]} than in {lo[0]}.")
    shares = [100 * r[1] / r[3] for r in rows]
    print(f"On-site cooling is only {min(shares):.0f}-{max(shares):.0f} % of the total: "
          f"the electricity grid dominates.")
    low_l_high_s = [r[0] for r in rows[:4] if r[4] >= 3]
    if low_l_high_s:
        print(f"Careful: {', '.join(low_l_high_s)} use little water but have High water stress.")

    if max_stress is not None:
        ok = [r for r in rows if r[4] <= max_stress]
        picks = ", ".join(f"{r[0]} ({r[3]:.3f} mL)" for r in ok[:3])
        print(f"\n{BOLD}Recommended{RESET} with water stress <= {max_stress}: {picks}")

    if scale:
        print(f"\n{BOLD}If this job ran {scale:,} times{RESET} {GREY}(linear scaling){RESET}:")
        for region, _, _, tot, _ in (rows[0], rows[len(rows) // 2], rows[-1]):
            print(f"  {region:12} {fmt_ml(tot * scale)}")

    print(f"\n{GREY}Estimates for comparison, not a measurement of any real facility.{RESET}\n")
    return m
