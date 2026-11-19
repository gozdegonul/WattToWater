"""Team report: summarise a water log as Markdown (for a terminal, a PR or CI).

    python -m watttowater report water_log.csv --region Virginia

Inside GitHub Actions the summary is also written to the job summary page
($GITHUB_STEP_SUMMARY), so every pipeline run shows its water footprint.
"""

import csv
import os
from collections import OrderedDict

from .data import REGIONS, STRESS, STRESS_SHORT, stress_class, water_for


def load_log(path):
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def summarize(path, region=None):
    """Return a Markdown summary of the runs in a water log."""
    rows = load_log(path)
    if not rows:
        return "No runs in the water log yet."

    jobs = OrderedDict()
    for r in rows:
        j = jobs.setdefault(r["name"], {"runs": 0, "energy": 0.0, "time": 0.0})
        j["runs"] += 1
        j["energy"] += float(r["energy_kwh"])
        j["time"] += float(r["duration_s"])
    total_e = sum(j["energy"] for j in jobs.values())

    totals = {g: water_for(g, total_e)[2] * 1000 for g in REGIONS}
    lo = min(totals, key=totals.get)
    hi = max(totals, key=totals.get)

    out = ["## Water footprint of this run (WattToWater)", ""]
    out.append(f"**{len(rows)} measured runs, {total_e:.2e} kWh in total.** "
               f"The same work needs **{totals[lo]:.3f} mL** in {lo} and "
               f"**{totals[hi]:.3f} mL** in {hi} ({totals[hi] / totals[lo]:.1f}x).")
    if region:
        score = STRESS[region][0]
        out.append(f"In **{region}** it is **{totals[region]:.3f} mL**, at water stress "
                   f"{score:.2f} ({STRESS_SHORT[stress_class(score)]}).")
    out.append("")

    col = region or "US average"
    out.append(f"| Job | Runs | Time (s) | Energy (kWh) | Water in {col} (mL) | Share |")
    out.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for name, j in sorted(jobs.items(), key=lambda kv: -kv[1]["energy"]):
        w = water_for(col, j["energy"])[2] * 1000
        out.append(f"| {name} | {j['runs']} | {j['time']:.2f} | {j['energy']:.2e} | "
                   f"{w:.3f} | {100 * j['energy'] / total_e:.0f}% |")
    biggest = max(jobs, key=lambda n: jobs[n]["energy"])
    out += ["", f"Largest consumer: **{biggest}** "
                f"({100 * jobs[biggest]['energy'] / total_e:.0f}% of the water).",
            "",
            "_Estimates: energy from CPU utilisation (linear power model); water factors from "
            "Li et al., arXiv:2304.03271; water stress from WRI Aqueduct 4.0._"]
    return "\n".join(out)


def write_github_summary(markdown):
    """Append the summary to the GitHub Actions job summary, if running in Actions."""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return False
    with open(path, "a", encoding="utf-8") as f:
        f.write(markdown + "\n")
    return True
