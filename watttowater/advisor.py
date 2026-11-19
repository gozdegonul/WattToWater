"""Decision support: where to run a job, and how big a model to run.

    from watttowater import recommend_regions, compare

    recommend_regions(max_stress=2.0)            # regions ranked by litres, stress <= 2
    compare({"100 trees": job100, "200 trees": job200})   # water vs result of variants
"""

from .data import REGIONS, STRESS, STRESS_SHORT, stress_class, water_for
from .meter import measure


def recommend_regions(energy_kwh=1.0, max_stress=None):
    """All regions ranked by total water, with stress and whether they pass max_stress.

    energy_kwh : energy of the job (default 1 kWh, i.e. litres per kWh)
    max_stress : optional policy limit on WRI Aqueduct baseline water stress (0-5)
    """
    rows = []
    for region in REGIONS:
        onsite, offsite, total = water_for(region, energy_kwh)
        score, category, level = STRESS[region]
        rows.append({
            "region": region,
            "water_l": total,
            "onsite_share": onsite / total,
            "stress": score,
            "stress_class": STRESS_SHORT[stress_class(score)],
            "allowed": max_stress is None or score <= max_stress,
        })
    rows.sort(key=lambda r: r["water_l"])
    return rows


def print_regions(energy_kwh=1.0, max_stress=None, unit="L"):
    """Print the region ranking as a table (litres or mL)."""
    scale = 1000 if unit == "mL" else 1
    rows = recommend_regions(energy_kwh, max_stress)
    print(f"{'Region':12} {'Water':>10}  {'On-site':>7}  {'Stress':>6}  {'':9} Policy")
    for r in rows:
        mark = "ok" if r["allowed"] else "over limit"
        print(f"{r['region']:12} {r['water_l'] * scale:7.3f} {unit:2}  "
              f"{100 * r['onsite_share']:6.1f}%  {r['stress']:6.2f}  {r['stress_class']:9} {mark}")
    ok = [r for r in rows if r["allowed"]]
    if max_stress is not None:
        print(f"\nPolicy: water stress <= {max_stress}. {len(ok)} of {len(rows)} regions pass.")
    if ok:
        best = ok[0]
        print(f"Best choice: {best['region']} ({best['water_l'] * scale:.3f} {unit}, "
              f"stress {best['stress']:.2f} {best['stress_class']})")
    return rows


def compare(jobs, repeats=1, baseline=None, region="US average"):
    """Measure several variants of a job and compare their water and their result.

    jobs     : {label: callable}; each callable returns a quality score (e.g. accuracy)
    repeats  : runs per variant (mean energy is used)
    baseline : label to compare against (default: the variant with the most energy)
    region   : region used for the litres column
    """
    rows = []
    for label, job in jobs.items():
        runs = [measure(job) for _ in range(repeats)]
        energy = sum(r["energy_kwh"] for r in runs) / repeats
        rows.append({"variant": label, "result": runs[-1]["result"], "energy_kwh": energy,
                     "water_ml": water_for(region, energy)[2] * 1000})
    ref = (next(r for r in rows if r["variant"] == baseline) if baseline
           else max(rows, key=lambda r: r["energy_kwh"]))
    for r in rows:
        r["water_pct"] = 100 * r["energy_kwh"] / ref["energy_kwh"]

    print(f"{'Variant':14} {'Result':>8} {'Energy (kWh)':>13} {'Water (' + region + ')':>22} "
          f"{'vs ' + ref['variant']:>14}")
    for r in rows:
        res = f"{r['result']:.4f}" if isinstance(r["result"], (int, float)) else str(r["result"])
        print(f"{r['variant']:14} {res:>8} {r['energy_kwh']:13.2e} {r['water_ml']:19.3f} mL "
              f"{r['water_pct']:13.0f}%")

    numeric = [r for r in rows if isinstance(r["result"], (int, float))]
    if numeric:
        best_q = max(r["result"] for r in numeric)
        # cheapest variant within 0.5 percentage points of the best result
        good = [r for r in numeric if r["result"] >= best_q - 0.005]
        pick = min(good, key=lambda r: r["energy_kwh"])
        print(f"\nSuggestion: {pick['variant']} reaches {pick['result']:.4f} "
              f"(best {best_q:.4f}) with {pick['water_pct']:.0f}% of the water of "
              f"{ref['variant']}.")
    return rows
