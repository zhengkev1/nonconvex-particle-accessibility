"""Draw every shape in accessibility.shapes, grouped by family, with a few parameter values.

Output: figures/shape_gallery.png
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from accessibility import make
from accessibility.plotting import draw

COLORS = {"convex reference": "#868e96", "cavity (curved)": "#4c6ef5",
          "cavity (straight)": "#e8590c", "arms and hooks": "#2f9e44"}

ROWS = [
    ("convex reference", [("disc", {}), ("ellipse", {"aspect": 1.5}), ("ellipse", {"aspect": 3})]),
    ("cavity (curved)", [("sector", {"mouth_deg": 60}), ("c_shape", {"mouth_deg": 10}),
                         ("c_shape", {"mouth_deg": 60}), ("ring_segment", {"thickness": 0.4}),
                         ("crescent", {"offset": 0.4})]),
    ("cavity (straight)", [("u_shape", {"depth": 0.6}), ("u_shape", {"depth": 1.4}),
                           ("l_shape", {}), ("t_shape", {}), ("s_shape", {})]),
    ("arms and hooks", [("plus", {}), ("hooked_cross", {"hook_len": 0.5}),
                        ("hooked_cross", {"hook_len": 1.2}), ("star", {"points": 5}),
                        ("star", {"points": 8, "inner_ratio": 0.6})]),
]


def label(name, params):
    if not params:
        return name
    return name + "\n" + ", ".join(f"{k}={v:g}" for k, v in params.items())


if __name__ == "__main__":
    ncol = max(len(items) for _, items in ROWS)
    fig, axes = plt.subplots(len(ROWS), ncol, figsize=(2.3 * ncol, 2.5 * len(ROWS)))
    for r, (family, items) in enumerate(ROWS):
        for c in range(ncol):
            ax = axes[r, c]
            ax.axis("off")
            if c >= len(items):
                continue
            name, params = items[c]
            draw(ax, make(name, **params), COLORS[family], alpha=0.9)
            ax.set_title(label(name, params), fontsize=8)
            ax.set_xlim(-1.7, 1.7)
            ax.set_ylim(-1.7, 1.7)
            ax.set_aspect("equal")
        axes[r, 0].text(-2.1, 0, family, rotation=90, va="center", ha="right", fontsize=10)
    fig.suptitle("Shape library (accessibility/shapes.py)", fontsize=12)
    fig.tight_layout()
    fig.savefig("figures/shape_gallery.png", dpi=150, bbox_inches="tight")
    print("saved figures/shape_gallery.png")
