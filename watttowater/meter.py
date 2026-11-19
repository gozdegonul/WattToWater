"""Energy estimate from CPU utilisation.

ASSUMPTIONS (not measurements):
    P = IDLE_W + (TDP_W - IDLE_W) * u      u = average system-wide CPU utilisation (0..1)
    E = P * t / 3,600,000                  kWh
TDP_W defaults to 45 W, the processor base power Intel lists for the Core i5-12450H used in
the paper. IDLE_W defaults to 5 W, our own assumption. Set both for your machine with the
environment variables WATTTOWATER_TDP_W and WATTTOWATER_IDLE_W.
"""

import os
import time

import psutil

TDP_W = float(os.environ.get("WATTTOWATER_TDP_W", 45))
IDLE_W = float(os.environ.get("WATTTOWATER_IDLE_W", 5))


def power_w(util_pct, tdp_w=None, idle_w=None):
    tdp = TDP_W if tdp_w is None else tdp_w
    idle = IDLE_W if idle_w is None else idle_w
    return idle + (tdp - idle) * util_pct / 100


class Meter:
    """Measures wall time and average CPU utilisation between start() and stop().

    The power model is linear, so the average utilisation over the run gives the same
    energy as sampling it many times: one reading at the start and one at the end suffice.
    """

    def start(self):
        psutil.cpu_percent(None)          # reset the counter; the first value is meaningless
        self._t0 = time.perf_counter()
        return self

    def stop(self):
        duration_s = time.perf_counter() - self._t0
        util = psutil.cpu_percent(None)   # average utilisation since start()
        p = power_w(util)
        return {
            "duration_s": duration_s,
            "util_pct": util,
            "power_w": p,
            "energy_kwh": p * duration_s / 3_600_000,
        }


def measure(job):
    """Run job() and return its result with duration, utilisation, power and energy."""
    meter = Meter().start()
    result = job()
    m = meter.stop()
    m["result"] = result
    return m
