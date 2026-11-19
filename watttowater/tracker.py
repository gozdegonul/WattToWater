"""One-line water tracking for any piece of Python code.

    from watttowater import track_water

    @track_water                       # decorator: every call is measured
    def train(): ...

    @track_water(region="Virginia")    # name the region you deploy to
    def train(): ...

    with track_water("nightly-train") as t:    # or any block of code
        ...
    print(t.water_ml)

Each run prints a one-line report and is appended to a CSV log (default water_log.csv,
or the path in WATTTOWATER_LOG; pass log=False to switch it off). The log feeds
`python -m watttowater report`.
"""

import csv
import functools
import os
from datetime import datetime

from .data import REGIONS, STRESS, STRESS_SHORT, stress_class, water_for
from .meter import IDLE_W, TDP_W, Meter

DEFAULT_LOG = "water_log.csv"
LOG_COLUMNS = (["timestamp", "name", "duration_s", "util_pct", "power_w", "energy_kwh",
                "tdp_w", "idle_w"] + [f"water_ml_{r}" for r in REGIONS])


def _log_path(log):
    if log is False or log is None:
        return None
    if log is True:
        return os.environ.get("WATTTOWATER_LOG", DEFAULT_LOG)
    return str(log)


def append_log(path, name, m):
    """Append one measured run to the CSV log."""
    new_file = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(LOG_COLUMNS)
        row = [datetime.now().isoformat(timespec="seconds"), name,
               round(m["duration_s"], 4), round(m["util_pct"], 1), round(m["power_w"], 2),
               f"{m['energy_kwh']:.9f}", TDP_W, IDLE_W]
        row += [round(water_for(r, m["energy_kwh"])[2] * 1000, 5) for r in REGIONS]
        w.writerow(row)


def one_line_report(name, m, region=None):
    """Short human-readable report of one run."""
    e = m["energy_kwh"]
    totals = {r: water_for(r, e)[2] * 1000 for r in REGIONS}
    lo = min(totals, key=totals.get)
    hi = max(totals, key=totals.get)
    text = (f"[WattToWater] {name}: {m['duration_s']:.2f} s, {e:.2e} kWh -> "
            f"{totals[lo]:.3f} mL ({lo}) to {totals[hi]:.3f} mL ({hi})")
    if region:
        score = STRESS[region][0]
        text += (f" | {region}: {totals[region]:.3f} mL, water stress "
                 f"{score:.2f} {STRESS_SHORT[stress_class(score)]}")
    return text


class _Tracker:
    def __init__(self, name, region, log, quiet):
        if region is not None and region not in REGIONS:
            raise ValueError(f"Unknown region {region!r}. Choose from: {', '.join(REGIONS)}")
        self.name = name or "job"
        self.region = region
        self.log = _log_path(log)
        self.quiet = quiet
        self.measurement = None

    # --- context manager
    def __enter__(self):
        self._meter = Meter().start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.measurement = self._meter.stop()
        if exc_type is None:          # failed runs are not reported or logged
            if self.log:
                append_log(self.log, self.name, self.measurement)
            if not self.quiet:
                print(one_line_report(self.name, self.measurement, self.region))
        return False

    # --- results
    @property
    def energy_kwh(self):
        return self.measurement["energy_kwh"]

    @property
    def water_ml(self):
        """Total water in mL per region for the last run."""
        return {r: water_for(r, self.energy_kwh)[2] * 1000 for r in REGIONS}

    # --- decorator
    def __call__(self, func):
        name = self.name if self.name != "job" else func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with _Tracker(name, self.region, self.log, self.quiet) as t:
                out = func(*args, **kwargs)
            wrapper.last_run = t
            return out

        wrapper.last_run = None
        return wrapper


def track_water(name=None, *, region=None, log=True, quiet=False):
    """Measure the water footprint of a function (decorator) or a block (context manager).

    name   : label in the report and the log (default: the function name)
    region : the region you deploy to; adds its litres and water stress to the report
    log    : True (default) -> water_log.csv or $WATTTOWATER_LOG; a path; or False
    quiet  : True to skip the printed report
    """
    if callable(name):                 # used bare: @track_water
        return _Tracker(None, region, log, quiet)(name)
    return _Tracker(name, region, log, quiet)
