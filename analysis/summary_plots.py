"""Combine the saved results into one summary figure.

Reads results/c_shape_vs_mouth_angle.csv and results/cross_hook_accessibility.csv.
Output: figures/results_summary.png
"""
import matplotlib.pyplot as plt
import pandas as pd

c = pd.read_csv("results/c_shape_vs_mouth_angle.csv")
x = pd.read_csv("results/cross_hook_accessibility.csv")
xh = x.dropna(subset=["height_change"])

fig, ax = plt.subplots(1, 3, figsize=(14, 4.2))

ax[0].plot(c.mouth_angle_deg, c.inaccessibility, "o-", ms=3)
ax[0].set_xlabel("Mouth angle φ (degrees)")
ax[0].set_ylabel("Inaccessibility index I")
ax[0].set_title("C-shape: inaccessible fraction vs opening")

ax[1].plot(x.hook_len, x.accessible_fraction, "s-", color="#2f9e44")
ax[1].set_xlabel("Hook length (shape units)")
ax[1].set_ylabel("Accessible fraction (accessible area / domain)")
ax[1].set_title("Cross with hooks: accessible fraction vs hook length")

ax[2].scatter(xh.height_change, xh.accessible_fraction, color="#c92a2a", s=50)
for _, r in xh.iterrows():
    ax[2].annotate(f"{r.hook_len:g}", (r.height_change, r.accessible_fraction),
                   textcoords="offset points", xytext=(5, 4), fontsize=8)
ax[2].set_xlabel("Change of bed height in DEM settling run")
ax[2].set_ylabel("Accessible fraction")
ax[2].set_title("Cross: accessible fraction vs settling (labels = hook length)")

for a in ax:
    a.grid(True, alpha=0.4)
fig.tight_layout()
fig.savefig("figures/results_summary.png", dpi=160, bbox_inches="tight")
print("saved figures/results_summary.png")
rank_corr = xh.accessible_fraction.rank().corr(xh.height_change.rank())
print("Spearman rank correlation (accessible fraction, height change):", round(rank_corr, 3))
