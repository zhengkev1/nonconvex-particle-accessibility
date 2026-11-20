"""Draw every particle shape family used in this repository on one figure.

The shape definitions repeat the ones in c_shape/ and cross_shape/ so this
script can run on its own (those scripts start their sweeps on import).
Output: figures/shape_gallery.png
"""
import math

import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union


def sector(radius=1.0, mouth_deg=30.0, segments=100):
    """Pac-Man: a disc with a wedge of angle mouth_deg removed."""
    t = math.radians(mouth_deg / 2)
    arc = [(radius * math.cos(a), radius * math.sin(a))
           for a in np.linspace(t, 2 * math.pi - t, segments)]
    return Polygon([(0, 0)] + arc + [(0, 0)])


def c_shape(mouth_deg=30.0, inner_radius=0.75):
    """C-shape: the sector minus an inner disc."""
    inner = Polygon([(inner_radius * math.cos(a), inner_radius * math.sin(a))
                     for a in np.linspace(0, 2 * math.pi, 100)])
    return sector(1.0, mouth_deg).difference(inner)


def hooked_cross(hook_len=0.75, bar_len=1.5, bar_thk=0.3, hook_thk=0.3):
    """Cross with a rectangular hook across the end of each arm."""
    hl, ht, hh = bar_len / 2, bar_thk / 2, hook_len / 2
    parts = [
        Polygon([(-hl, -ht), (hl, -ht), (hl, ht), (-hl, ht)]),
        Polygon([(-ht, -hl), (ht, -hl), (ht, hl), (-ht, hl)]),
        Polygon([(-hh, hl), (hh, hl), (hh, hl + hook_thk), (-hh, hl + hook_thk)]),
        Polygon([(-hh, -hl - hook_thk), (hh, -hl - hook_thk), (hh, -hl), (-hh, -hl)]),
        Polygon([(-hl - hook_thk, -hh), (-hl, -hh), (-hl, hh), (-hl - hook_thk, hh)]),
        Polygon([(hl, -hh), (hl + hook_thk, -hh), (hl + hook_thk, hh), (hl, hh)]),
    ]
    return unary_union(parts)


def draw(ax, shape, color):
    x, y = shape.exterior.xy
    ax.fill(x, y, fc=color, ec="black", lw=0.6)
    for ring in shape.interiors:
        xi, yi = ring.xy
        ax.fill(xi, yi, fc="white", ec="black", lw=0.6)


ROWS = [
    ("Pac-Man (sector)", "#e0a526",
     [(f"mouth {m}°", sector(1.0, m)) for m in (10, 30, 60, 90)]),
    ("C-shape (sector minus inner disc)", "#4c6ef5",
     [(f"mouth {m}°", c_shape(m)) for m in (5, 24, 45, 90)]),
    ("Cross with hooks", "#2f9e44",
     [(f"hook length {h}", hooked_cross(h)) for h in (0.5, 0.75, 1.0, 1.2)]),
]

if __name__ == "__main__":
    fig, axes = plt.subplots(len(ROWS), 4, figsize=(10, 7.8))
    for r, (family, color, items) in enumerate(ROWS):
        for c, (label, shape) in enumerate(items):
            ax = axes[r, c]
            draw(ax, shape, color)
            ax.set_title(label, fontsize=9)
            ax.set_xlim(-1.3, 1.3)
            ax.set_ylim(-1.3, 1.3)
            ax.set_aspect("equal")
            ax.axis("off")
        axes[r, 0].text(-1.55, 0, family, rotation=90, va="center", ha="right", fontsize=10)
    fig.suptitle("Particle shape families", fontsize=12)
    fig.tight_layout()
    fig.savefig("figures/shape_gallery.png", dpi=160, bbox_inches="tight")
    print("saved figures/shape_gallery.png")
