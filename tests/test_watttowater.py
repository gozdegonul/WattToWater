"""Tests: the water model reproduces the numbers in the paper.

    python -m pytest tests
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from watttowater import recommend_regions, summarize, track_water, water_for  # noqa: E402
from watttowater.data import REGIONS, STRESS  # noqa: E402
from watttowater.meter import power_w  # noqa: E402

E_PAPER = 5.963e-05     # mean energy of the 15 runs in the paper (kWh)


def test_eleven_regions_with_stress():
    assert len(REGIONS) == 11
    assert set(REGIONS) == set(STRESS)


@pytest.mark.parametrize("region, l_per_kwh", [
    ("Ireland", 1.776), ("Texas", 1.897), ("Netherlands", 3.987), ("Washington", 11.876),
])
def test_total_water_per_kwh_matches_table_1(region, l_per_kwh):
    assert water_for(region, 1.0)[2] == pytest.approx(l_per_kwh, abs=1e-3)


def test_paper_headline_numbers():
    ml = {r: water_for(r, E_PAPER)[2] * 1000 for r in REGIONS}
    assert ml["Ireland"] == pytest.approx(0.106, abs=5e-4)
    assert ml["Washington"] == pytest.approx(0.708, abs=5e-4)
    assert ml["Washington"] / ml["Ireland"] == pytest.approx(6.7, abs=0.05)


def test_offsite_is_at_least_78_percent_everywhere():
    for r in REGIONS:
        onsite, offsite, total = water_for(r, 1.0)
        assert offsite / total >= 0.78


def test_power_model():
    assert power_w(0, 45, 5) == 5
    assert power_w(100, 45, 5) == 45
    assert power_w(50, 45, 5) == 25


def test_recommend_regions_policy():
    rows = recommend_regions(max_stress=2.0)
    assert rows[0]["region"] == "Ireland"                        # fewest litres
    texas = next(r for r in rows if r["region"] == "Texas")
    assert texas["allowed"] is False                              # stress 3.33 > 2
    assert [r["water_l"] for r in rows] == sorted(r["water_l"] for r in rows)


def test_tracker_logs_and_reports(tmp_path):
    log = tmp_path / "log.csv"

    @track_water(region="Iowa", log=log, quiet=True)
    def work():
        return sum(i * i for i in range(200_000))

    assert work() == sum(i * i for i in range(200_000))          # result passes through
    work()
    assert work.last_run.energy_kwh > 0
    with track_water("block", log=log, quiet=True) as t:
        sum(range(100_000))
    assert t.water_ml["Washington"] > t.water_ml["Ireland"]

    md = summarize(log, region="Iowa")
    assert "3 measured runs" in md
    assert "| work | 2 |" in md and "| block | 1 |" in md


def test_unknown_region_is_rejected():
    with pytest.raises(ValueError):
        track_water("x", region="Atlantis")
