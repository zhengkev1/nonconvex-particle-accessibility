"""Accessibility of the space around a fixed particle.

Same method as the original research scripts (c_shape/inaccessibility_sweep.py):

1. Fix one copy of the particle at the origin.
2. Place a second copy at every (x, y, theta) on a grid, rotating about the origin
   and then translating, and keep the placements that do not overlap the fixed one.
3. The union of the kept placements, clipped to a circular domain, is the
   accessible area. I = (domain - particle - accessible) / domain.

The overlap test is vectorised with Shapely 2, which is what makes batch sweeps
over many shapes practical.
"""
from __future__ import annotations

import math
import time
from dataclasses import asdict, dataclass

import numpy as np
import shapely
from shapely.affinity import rotate
from shapely.geometry import Polygon


@dataclass(frozen=True)
class Grid:
    """Sampling grid for the trial particle."""

    domain_radius: float = 2.5
    dx: float = 0.2            # translation step (shape units)
    dtheta_deg: float = 4.0    # rotation step (degrees)
    domain_segments: int = 100  # polygon resolution of the circular domain
    grid_start: float | None = None  # first x/y value; default -domain_radius
    grid_stop: float | None = None   # last x/y value (exclusive); default domain_radius + 0.01

    def xs(self) -> np.ndarray:
        r = self.domain_radius
        start = -r if self.grid_start is None else self.grid_start
        stop = r + 0.01 if self.grid_stop is None else self.grid_stop
        return np.arange(start, stop, self.dx)

    def angles(self) -> np.ndarray:
        return np.arange(0, 360, self.dtheta_deg)

    def domain(self) -> Polygon:
        r = self.domain_radius
        arc = [(r * math.cos(a), r * math.sin(a))
               for a in np.linspace(0, 2 * math.pi, self.domain_segments)]
        return Polygon([(0, 0)] + arc + [(0, 0)])


@dataclass
class Result:
    inaccessibility: float      # (domain - particle - accessible) / domain
    accessibility: float        # 1 - inaccessibility
    accessible_fraction: float  # accessible / domain (the "I" printed by cross_hook_sweep.py)
    accessible_area: float
    particle_area: float
    domain_area: float
    valid_placements: int
    total_placements: int
    seconds: float

    def as_dict(self) -> dict:
        return asdict(self)


def accessible_region(shape: Polygon, grid: Grid):
    """Return (union of non-overlapping placements, number valid, number tried)."""
    xs = grid.xs()
    xx, yy = np.meshgrid(xs, xs, indexing="ij")
    offsets = np.column_stack([xx.ravel(), yy.ravel()])
    shapely.prepare(shape)

    kept = []
    valid = tried = 0
    for angle in grid.angles():
        base = rotate(shape, float(angle), origin=(0, 0))
        trials = translated_copies(base, offsets)
        tried += len(trials)
        ok = ~shapely.intersects(trials, shape) & ~shapely.is_empty(trials)
        valid += int(ok.sum())
        if ok.any():
            # union per angle first: many medium unions are faster than one huge one
            kept.append(shapely.union_all(trials[ok]))
    union = shapely.union_all(np.array(kept, dtype=object)) if kept else Polygon()
    return union, valid, tried


def translated_copies(geom, offsets: np.ndarray) -> np.ndarray:
    """Independent copies of ``geom`` shifted by each row of ``offsets`` (vectorised)."""
    # object array: numpy's fixed-width bytes dtype would strip trailing zero bytes from the WKB
    wkb = np.empty(len(offsets), dtype=object)
    wkb[:] = [shapely.to_wkb(geom)] * len(offsets)
    copies = shapely.from_wkb(wkb)
    coords, index = shapely.get_coordinates(copies, return_index=True)
    return shapely.set_coordinates(copies, coords + offsets[index])


def compute(shape: Polygon, grid: Grid = Grid(), return_region: bool = False):
    """Accessibility of ``shape`` on ``grid``.

    With ``return_region=True`` returns ``(Result, accessible_region)`` so callers
    can plot the region without computing it twice.
    """
    t0 = time.perf_counter()
    union, valid, tried = accessible_region(shape, grid)
    domain = grid.domain()
    region = union.intersection(domain) if not union.is_empty else Polygon()
    acc = region.area
    I = (domain.area - shape.area - acc) / domain.area
    res = Result(
        inaccessibility=I,
        accessibility=1.0 - I,
        accessible_fraction=acc / domain.area,
        accessible_area=acc,
        particle_area=shape.area,
        domain_area=domain.area,
        valid_placements=valid,
        total_placements=tried,
        seconds=time.perf_counter() - t0,
    )
    return (res, region) if return_region else res
