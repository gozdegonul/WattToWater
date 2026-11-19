"""Regional water factors and water stress: the single source of truth.

Water factors (PUE, WUE, EWIF) per region:
    P. Li, J. Yang, M. A. Islam, S. Ren, "Making AI Less 'Thirsty'",
    arXiv:2304.03271, Table 1. Only the 11 operating regions are included;
    the 7 regions marked as under construction (projections) are excluded.

Water stress per region:
    WRI Aqueduct 4.0 Country Rankings, file Aqueduct40_rankings_download_Y2023M07D05.xlsx,
    indicator bws (baseline water stress), weight Tot (total demand), score 0-5.
    Country level (sheet country_baseline) for the Netherlands, Ireland, Sweden and the
    U.S. average; state level (sheet province_baseline) for the U.S. states.
    WRI notes that these indicators cannot be measured directly, have not been validated
    and do not model interbasin transfers.
"""

# region: (PUE, WUE in L/kWh, EWIF in L/kWh)
REGIONS = {
    "Netherlands": (1.140, 0.060, 3.445),
    "Arizona":     (1.180, 1.630, 4.959),
    "Ireland":     (1.190, 0.020, 1.476),
    "US average":  (1.170, 0.550, 3.142),
    "Illinois":    (1.350, 0.740, 2.233),
    "Iowa":        (1.160, 0.140, 3.104),
    "Texas":       (1.280, 0.250, 1.287),
    "Virginia":    (1.140, 0.140, 2.385),
    "Washington":  (1.150, 0.950, 9.501),
    "Wyoming":     (1.110, 0.130, 2.574),
    "Sweden":      (1.160, 0.090, 6.019),
}

# region: (bws score 0-5, category, level)
STRESS = {
    "Netherlands": (1.581120297, "Low - Medium (10-20%)", "country"),
    "Arizona":     (4.392122413, "Extremely High (>80%)", "state"),
    "Ireland":     (0.363338153, "Low (<10%)", "country"),
    "US average":  (2.604411175, "Medium - High (20-40%)", "country"),
    "Illinois":    (2.402912456, "Medium - High (20-40%)", "state"),
    "Iowa":        (1.08236803, "Low - Medium (10-20%)", "state"),
    "Texas":       (3.329698739, "High (40-80%)", "state"),
    "Virginia":    (2.562448902, "Medium - High (20-40%)", "state"),
    "Washington":  (1.203172775, "Low - Medium (10-20%)", "state"),
    "Wyoming":     (3.765395727, "High (40-80%)", "state"),
    "Sweden":      (0.781293393, "Low (<10%)", "country"),
}

STRESS_SHORT = ["Low", "Low-Med", "Med-High", "High", "Extreme"]


def stress_class(score):
    """Aqueduct 0-5 score -> category index 0..4 (one point per category)."""
    return min(int(score), 4)


def water_for(region, energy_kwh):
    """Water footprint in litres: (on-site, off-site, total).

    W = E * WUE + E * PUE * EWIF
    """
    pue, wue, ewif = REGIONS[region]
    onsite = energy_kwh * wue
    offsite = energy_kwh * pue * ewif
    return onsite, offsite, onsite + offsite
