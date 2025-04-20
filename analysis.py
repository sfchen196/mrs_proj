"""
analysis.py
Analyse boid‑flocking batch‑simulation results
=============================================

 * Expects results.csv produced by experiments.py / batch_sim.py
 * Computes Δ front and radial metrics vs. parameter change
 * Saves publication‑ready plots (PNG) without opening any GUI windows

Author: ChatGPT‑refactor
--------------------------------------------------------------------
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")           # head‑less back‑end, no pop‑ups
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

# ------------------------------------------------------------------
# 1. Load and sanity‑check the data
# ------------------------------------------------------------------
RESULTS_CSV = Path("results.csv")
if not RESULTS_CSV.exists():
    raise FileNotFoundError(
        "results.csv not found – run experiments.py to generate it first."
    )

df = pd.read_csv(RESULTS_CSV)

# Normalise column names if the script version changed
col_map = {
    "parameter": "param_name",
    "param": "param_name",
    "param_value": "param_val",
    "value": "param_val",
}
df.rename(columns={old: new for old, new in col_map.items() if old in df.columns},
          inplace=True)

for needed in ["param_name", "param_val", "delta_front", "delta_radial"]:
    if needed not in df.columns:
        raise ValueError(f"Column '{needed}' is missing from results.csv")

# ------------------------------------------------------------------
# 2. Add percent‑change column (relative to default value)
# ------------------------------------------------------------------
DEFAULTS = {
    "MAX_SPEED": 3.0,
    "SEPARATION_RADIUS": 30.0,
    "COHESION_WEIGHT": 0.005,
}
def pct_change(row):
    base = DEFAULTS.get(row["param_name"])
    if base is None:
        return np.nan
    return 100.0 * (row["param_val"] - base) / base

df["pct_change"] = df.apply(pct_change, axis=1)

# ------------------------------------------------------------------
# 3. Helper – line with 95 % CI (pure Matplotlib, safe for pandas 2.x)
# ------------------------------------------------------------------
def plot_mean_ci(ax, sub, xcol, ycol, label, color):
    """Plot mean ± 95 % CI for each unique x value."""
    sub = sub.dropna(subset=[xcol, ycol])
    xs = np.sort(sub[xcol].unique())
    means, lo, hi = [], [], []
    for x in xs:
        vals = sub.loc[sub[xcol] == x, ycol].to_numpy()
        m = vals.mean()
        if len(vals) > 1:
            se = vals.std(ddof=1) / np.sqrt(len(vals))
            ci95 = 1.96 * se
        else:
            ci95 = 0.0
        means.append(m)
        lo.append(m - ci95)
        hi.append(m + ci95)
    ax.plot(xs, means, marker="o", lw=1.8, color=color, label=label)
    ax.fill_between(xs, lo, hi, color=color, alpha=0.20)

# Colour cycle for parameters
COLORS = dict(
    MAX_SPEED="#1f77b4",
    SEPARATION_RADIUS="#ff7f0e",
    COHESION_WEIGHT="#2ca02c",
)

# ------------------------------------------------------------------
# 4. Combined figure: Δ front & Δ radial vs. % change
# ------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharex=True)
for pname, sub in df.groupby("param_name"):
    plot_mean_ci(
        axes[0], sub, "pct_change", "delta_front",
        label=pname.replace("_", " ").title(), color=COLORS.get(pname, None)
    )
    plot_mean_ci(
        axes[1], sub, "pct_change", "delta_radial",
        label=pname.replace("_", " ").title(), color=COLORS.get(pname, None)
    )

for ax, ylabel in zip(axes, ["Δ Front position (m)", "Δ Radial distance (m)"]):
    ax.axhline(0, color="gray", lw=0.8, ls="--")
    ax.set_xlabel("Parameter change (%)")
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=8, frameon=False)
fig.tight_layout()
fig.savefig("combined_metrics.png", dpi=300)
plt.close(fig)
print("✓ combined_metrics.png written")

# ------------------------------------------------------------------
# 5. Scatter + regression lines for each parameter separately
# ------------------------------------------------------------------
def save_scatter(param, metric, fname):
    sub = df[df["param_name"] == param].dropna(subset=["pct_change", metric])
    x = sub["pct_change"].to_numpy()
    y = sub[metric].to_numpy()
    rho, pval = spearmanr(x, y)
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.scatter(x, y, s=30, color=COLORS.get(param, "#333333"))
    # simple best‑fit (least squares) for visual cue
    if len(x) > 1:
        coeffs = np.polyfit(x, y, 1)
        xl = np.linspace(x.min(), x.max(), 100)
        ax.plot(xl, np.polyval(coeffs, xl), color="black", lw=1)
    ax.axhline(0, color="gray", lw=0.8, ls="--")
    ax.set_title(f"{param.replace('_',' ')}  ρ={rho:.2f}, p={pval:.3f}", fontsize=10)
    ax.set_xlabel("Parameter change (%)")
    ax.set_ylabel(metric.replace("delta_", "Δ ").title() + " (m)")
    fig.tight_layout()
    fig.savefig(fname, dpi=300)
    plt.close(fig)
    print(f"✓ {fname} written")

for param in df["param_name"].unique():
    save_scatter(param, "delta_front",  f"{param}_front_scatter.png")
    save_scatter(param, "delta_radial", f"{param}_radial_scatter.png")

print("All analysis plots saved.")
