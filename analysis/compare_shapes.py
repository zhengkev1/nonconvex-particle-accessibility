"""Compare shape families from a batch sweep (default results/all_shapes.csv).

One panel per swept parameter: inaccessibility index I against the parameter.
Also writes results/all_shapes_summary.csv with the range of I for each sweep.
Output: figures/compare_shapes.png
"""
import math
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from accessibility.shapes import FAMILIES

path = sys.argv[1] if len(sys.argv) > 1 else "results/all_shapes.csv"
d = pd.read_csv(path)
family_of = {s: f for f, names in FAMILIES.items() for s in names}
d["family"] = d["shape"].map(family_of)
d["sweep"] = d["shape"] + " vs " + d["param"]

summary = (d.groupby(["family", "sweep"])
             .agg(points=("inaccessibility", "size"),
                  I_min=("inaccessibility", "min"),
                  I_max=("inaccessibility", "max"),
                  seconds=("seconds", "sum"))
             .reset_index()
             .sort_values(["family", "I_max"], ascending=[True, False]))
summary.to_csv(path.replace(".csv", "_summary.csv"), index=False)
print(summary.round(4).to_string(index=False))

sweeps = [s for s in summary["sweep"] if (d["sweep"] == s).sum() > 1]
ncol = 4
nrow = math.ceil(len(sweeps) / ncol)
fig, axes = plt.subplots(nrow, ncol, figsize=(4 * ncol, 3.1 * nrow), squeeze=False)
colors = {"convex reference": "#868e96", "cavity (curved)": "#4c6ef5",
          "cavity (straight)": "#e8590c", "arms and hooks": "#2f9e44"}
for ax, s in zip(axes.flat, sweeps):
    g = d[d["sweep"] == s].sort_values("value")
    ax.plot(g["value"], g["inaccessibility"], "o-", color=colors[g["family"].iloc[0]], ms=4)
    ax.set_title(s, fontsize=9)
    ax.set_xlabel(g["param"].iloc[0], fontsize=8)
    ax.set_ylabel("I", fontsize=8)
    ax.grid(True, alpha=0.4)
for ax in list(axes.flat)[len(sweeps):]:
    ax.axis("off")
fig.suptitle("Inaccessibility index across shape families (colour = family)")
fig.tight_layout()
fig.savefig("figures/compare_shapes.png", dpi=140, bbox_inches="tight")
print("saved figures/compare_shapes.png")
