"""How much does the inaccessibility index depend on the sampling grid?

Recomputes I for a few shapes while refining the translation step and the
rotation step separately. Output: results/grid_convergence.csv and
figures/grid_convergence.png
"""
import csv
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from accessibility import Grid, compute, make

CASES = [("c_shape", {"mouth_deg": 24}), ("c_shape", {"mouth_deg": 45}),
         ("hooked_cross", {"hook_len": 0.75})]
DX = [0.4, 0.3, 0.2, 0.15, 0.1]
DTHETA = [12, 8, 4, 2]
BASE_DX, BASE_DTHETA, R = 0.2, 4, 2.5

if __name__ == "__main__":
    quick = "--quick" in sys.argv
    dx_list = DX[:3] if quick else DX
    dt_list = DTHETA[:3] if quick else DTHETA
    rows = []
    for name, params in CASES:
        shape = make(name, **params)
        tag = name + " " + ", ".join(f"{k}={v:g}" for k, v in params.items())
        for dx in dx_list:
            r = compute(shape, Grid(R, dx, BASE_DTHETA))
            rows.append({"case": tag, "vary": "dx", "dx": dx, "dtheta_deg": BASE_DTHETA,
                         "inaccessibility": r.inaccessibility, "seconds": r.seconds})
            print(tag, "dx", dx, round(r.inaccessibility, 5), f"{r.seconds:.1f}s", flush=True)
        for dt in dt_list:
            r = compute(shape, Grid(R, BASE_DX, dt))
            rows.append({"case": tag, "vary": "dtheta", "dx": BASE_DX, "dtheta_deg": dt,
                         "inaccessibility": r.inaccessibility, "seconds": r.seconds})
            print(tag, "dtheta", dt, round(r.inaccessibility, 5), f"{r.seconds:.1f}s", flush=True)

    with open("results/grid_convergence.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for name, params in CASES:
        tag = name + " " + ", ".join(f"{k}={v:g}" for k, v in params.items())
        a = [r for r in rows if r["case"] == tag and r["vary"] == "dx"]
        b = [r for r in rows if r["case"] == tag and r["vary"] == "dtheta"]
        ax[0].plot([r["dx"] for r in a], [r["inaccessibility"] for r in a], "o-", label=tag)
        ax[1].plot([r["dtheta_deg"] for r in b], [r["inaccessibility"] for r in b], "o-", label=tag)
    ax[0].set_xlabel(f"translation step dx (rotation step {BASE_DTHETA}°)")
    ax[1].set_xlabel(f"rotation step (degrees, dx = {BASE_DX})")
    for a_ in ax:
        a_.set_ylabel("Inaccessibility index I")
        a_.invert_xaxis()
        a_.grid(True, alpha=0.4)
        a_.legend(fontsize=8)
    fig.suptitle("Grid convergence: finer grid to the right")
    fig.tight_layout()
    fig.savefig("figures/grid_convergence.png", dpi=150, bbox_inches="tight")
    print("saved results/grid_convergence.csv and figures/grid_convergence.png")
