# WattToWater

**How much water does a piece of code use, and where should it run?**

WattToWater converts the energy of a compute job into litres of water, split into
on-site cooling water and off-site water used to generate the electricity, and
compares the result across 11 data-center regions side by side with WRI Aqueduct
baseline water stress.

![Water by region](figures/fig1_water_by_region.png)

## Key results (200-tree Random Forest, about 5.96 × 10⁻⁵ kWh per run)

| Finding | Number |
|---|---|
| Same job, best vs worst region | 0.106 mL (Ireland) vs 0.708 mL (Washington), **6.7×** |
| Share of water that is off-site (electricity) | at least **78 %** in every region |
| Litres and scarcity disagree | Texas: 2nd-lowest litres, **High** water stress |
| Smaller model | 100 trees: **48 %** of the energy and water, accuracy 96.15 % vs 95.90 % |

All numbers are estimates for comparison, not measurements of any real facility.
See the paper for assumptions and limitations.

## Quick start

```bash
py -m pip install -r requirements.txt
```

```bash
py watttowater.py
```

```bash
py watttowater.py --trees 50 --scale 1000000
```

```bash
py analysis.py
```

`watttowater.py` runs the job live and prints the 11-region comparison.
`analysis.py` regenerates every table (`outputs/`) and figure (`figures/`) in the
paper from the recorded runs, without measuring anything new.

## Method in one line

```
W = E · WUE  +  E · PUE · EWIF
    on-site     off-site (electricity generation)
```

`E` is estimated from CPU utilisation: `P = 5 W + (45 W − 5 W) · u`
(45 W = Intel processor base power for the i5-12450H; 5 W idle is an assumption).

## Files

| File | Purpose |
|---|---|
| `water2.py` | PUE, WUE, EWIF for 11 regions (Li et al., Table 1) and the water formula |
| `stress.py` | WRI Aqueduct 4.0 baseline water stress per region |
| `aquameter.py` | Measures a job: time, CPU utilisation, power, energy |
| `ml_job.py` | The benchmark job (Random Forest on synthetic data) |
| `log_runs.py` | Runs the job 5× and appends to `results.csv` |
| `tradeoff.py` | Model-size experiment (25–200 trees), writes `tradeoff.csv` |
| `analysis.py` | All paper tables and figures |
| `watttowater.py` | Live demo |
| `watttowater_map.html` | Interactive map (open in a browser) |

## Sources

- P. Li, J. Yang, M. A. Islam, S. Ren, *Making AI Less "Thirsty"*, arXiv:2304.03271, Table 1.
- WRI Aqueduct 4.0 Country Rankings, `Aqueduct40_rankings_download_Y2023M07D05.xlsx`.
- Intel Core i5-12450H product specifications, intel.com (processor base power 45 W).

Environment: Python 3.12.0, scikit-learn 1.3.2, NumPy 1.26.4, psutil 7.2.2, Windows 11.
