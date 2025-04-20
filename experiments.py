"""
experiments.py
==============

Runs the full parameter grid for:
    MAX_SPEED, SEPARATION_RADIUS, COHESION_WEIGHT
varying each from –50 % to +50 % (10 % step) relative to the
*default* values in config.py.  For every run it measures:

    - delta_front  : mean front/back shift of the selected group
    - delta_radial : mean radial shift of the selected group
    - run_time_s   : how long the trial lasted until centroid ≈ goal

and writes one line per trial to results/experiment_metrics.csv
with *consistent* column names that all plotting scripts will use.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import itertools, time
# ----------  your simulation imports  -------------
import config
from batch_sim import run_single_sim      # helper we wrote below
# ---------------------------------------------------

# ------------------------------------------------------------------
# utilities
# ------------------------------------------------------------------
def pct_range(steps=11):                   # –50 … +50 inclusive
    return np.linspace(-0.5, 0.5, steps)

DEFAULTS = dict(MAX_SPEED=config.MAX_SPEED,
                SEPARATION_RADIUS=config.SEPARATION_RADIUS,
                COHESION_WEIGHT=config.COHESION_WEIGHT)

PARAM_RANGE = {
    "MAX_SPEED"        : DEFAULTS["MAX_SPEED"]        * (1 + pct_range()),
    "SEPARATION_RADIUS": DEFAULTS["SEPARATION_RADIUS"]* (1 + pct_range()),
    "COHESION_WEIGHT"  : DEFAULTS["COHESION_WEIGHT"]  * (1 + pct_range()),
}

# ------------------------------------------------------------------
# experiment loop
# ------------------------------------------------------------------
out_dir = Path("results"); out_dir.mkdir(exist_ok=True)
csv_file = out_dir/"experiment_metrics.csv"
rows = []

for param_name, values in PARAM_RANGE.items():
    for value in values:
        pct_change = 100 * (value - DEFAULTS[param_name]) / DEFAULTS[param_name]

        # Build a *controlled* parameter dict: only the tested
        # parameter differs, everything else = default.
        params = DEFAULTS.copy()
        params[param_name] = value

        # ---------------  RUN THE SIM  --------------------------
        t0 = time.time()
        d_front, d_radial = run_single_sim(params)     # returns the two metrics
        dt = time.time() - t0
        # --------------------------------------------------------

        rows.append(dict(param_name = param_name,
                         param_value = value,
                         pct_change = pct_change,
                         delta_front = d_front,
                         delta_radial = d_radial,
                         run_time_s = dt))

        print(f"{param_name:18s} {pct_change:6.0f}%  "
              f"ΔFront={d_front:+5.2f}  ΔRadial={d_radial:+5.2f}")

df = pd.DataFrame(rows)
df.to_csv(csv_file, index=False)
print("\nSaved CSV to", csv_file)
