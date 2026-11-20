"""Library of 2D particle shapes.

Every shape is a Shapely polygon centred near the origin with an outer size of
about 1 (radius or half-length), so the same sweep settings work for all of
them. ``SHAPES`` maps a family name to its builder; each builder takes keyword
parameters with defaults, which is what the sweep configs vary.
"""
from __future__ import annotations

import math
from typing import Callable, Dict

import numpy as np
from shapely.affinity import rotate, scale, translate
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

SEGMENTS = 100


def _arc(radius: float, start: float, end: float, n: int = SEGMENTS):
    return [(radius * math.cos(a), radius * math.sin(a)) for a in np.linspace(start, end, n)]


def disc(radius: float = 1.0) -> Polygon:
    """Convex reference shape: every point outside it is reachable."""
    return Polygon(_arc(radius, 0, 2 * math.pi))


def sector(mouth_deg: float = 30.0, radius: float = 1.0) -> Polygon:
    """Pac-Man: a disc with a wedge of angle ``mouth_deg`` removed, mouth facing +x."""
    t = math.radians(mouth_deg / 2)
    return Polygon([(0, 0)] + _arc(radius, t, 2 * math.pi - t) + [(0, 0)])


def c_shape(mouth_deg: float = 30.0, inner_radius: float = 0.75, radius: float = 1.0) -> Polygon:
    """C-shape: the sector minus an inner disc (as in c_shape/inaccessibility_sweep.py)."""
    inner = Polygon([(0, 0)] + _arc(inner_radius, 0, 2 * math.pi) + [(0, 0)])
    return sector(mouth_deg, radius).difference(inner)


def hooked_cross(hook_len: float = 0.75, bar_len: float = 1.5, bar_thk: float = 0.3,
                 hook_thk: float = 0.3) -> Polygon:
    """Cross with a rectangular hook across each arm end (as in cross_shape/cross_hook_sweep.py)."""
    hl, ht, hh = bar_len / 2, bar_thk / 2, hook_len / 2
    parts = [
        box(-hl, -ht, hl, ht),
        box(-ht, -hl, ht, hl),
        box(-hh, hl, hh, hl + hook_thk),
        box(-hh, -hl - hook_thk, hh, -hl),
        box(-hl - hook_thk, -hh, -hl, hh),
        box(hl, -hh, hl + hook_thk, hh),
    ]
    return unary_union(parts)


def plus(arm_thk: float = 0.3, arm_len: float = 2.0) -> Polygon:
    """Plain plus sign (a hooked cross with no hooks)."""
    a, t = arm_len / 2, arm_thk / 2
    return unary_union([box(-a, -t, a, t), box(-t, -a, t, a)])


def star(points: int = 5, inner_ratio: float = 0.45, radius: float = 1.0) -> Polygon:
    """Star polygon with ``points`` tips; smaller ``inner_ratio`` means deeper notches."""
    coords = []
    for k in range(2 * points):
        r = radius if k % 2 == 0 else radius * inner_ratio
        a = math.pi / 2 + k * math.pi / points
        coords.append((r * math.cos(a), r * math.sin(a)))
    return Polygon(coords)


def ring_segment(gap_deg: float = 60.0, thickness: float = 0.25, radius: float = 1.0) -> Polygon:
    """Arc of an annulus with a gap of ``gap_deg``; like the C-shape but with variable wall thickness."""
    return c_shape(gap_deg, inner_radius=radius - thickness, radius=radius)


def l_shape(arm_ratio: float = 1.0, thickness: float = 0.4) -> Polygon:
    """L-shape: a vertical bar of height 2 and a horizontal foot of length 2*arm_ratio."""
    shape = unary_union([box(0, 0, thickness, 2.0), box(0, 0, 2.0 * arm_ratio, thickness)])
    return _centre(shape)


def t_shape(stem_ratio: float = 1.0, thickness: float = 0.4) -> Polygon:
    """T-shape: a bar of length 2 on top of a stem of length 2*stem_ratio."""
    shape = unary_union([box(-1, 0, 1, thickness), box(-thickness / 2, -2 * stem_ratio, thickness / 2, 0)])
    return _centre(shape)


def u_shape(depth: float = 1.2, width: float = 1.6, thickness: float = 0.3) -> Polygon:
    """U-shape (a staple): open cavity whose depth and width can be varied."""
    w = width / 2
    shape = unary_union([
        box(-w, 0, w, thickness),
        box(-w, 0, -w + thickness, depth),
        box(w - thickness, 0, w, depth),
    ])
    return _centre(shape)


def s_shape(thickness: float = 0.3, size: float = 1.6) -> Polygon:
    """Z/S-shape: two parallel bars joined by a diagonal-free vertical link."""
    s = size / 2
    shape = unary_union([
        box(-s, s - thickness, s / 3, s),
        box(-thickness / 2, -s, thickness / 2, s),
        box(-s / 3, -s, s, -s + thickness),
    ])
    return _centre(shape)


def crescent(offset: float = 0.4, cut_radius: float = 0.9, radius: float = 1.0) -> Polygon:
    """Crescent: a disc with a second, shifted disc removed."""
    cut = translate(disc(cut_radius), xoff=offset)
    shape = disc(radius).difference(cut)
    return _largest(shape)


def ellipse(aspect: float = 2.0) -> Polygon:
    """Convex ellipse with semi-axes 1 and 1/aspect."""
    return scale(Point(0, 0).buffer(1.0, 64), xfact=1.0, yfact=1.0 / aspect)


def _centre(shape: Polygon) -> Polygon:
    c = shape.centroid
    return translate(shape, xoff=-c.x, yoff=-c.y)


def _largest(shape):
    if shape.geom_type == "MultiPolygon":
        return max(shape.geoms, key=lambda g: g.area)
    return shape


SHAPES: Dict[str, Callable[..., Polygon]] = {
    "disc": disc,
    "ellipse": ellipse,
    "sector": sector,
    "c_shape": c_shape,
    "ring_segment": ring_segment,
    "crescent": crescent,
    "hooked_cross": hooked_cross,
    "plus": plus,
    "star": star,
    "l_shape": l_shape,
    "t_shape": t_shape,
    "u_shape": u_shape,
    "s_shape": s_shape,
}

# Short grouping used by the gallery and README.
FAMILIES = {
    "convex reference": ["disc", "ellipse"],
    "cavity (curved)": ["sector", "c_shape", "ring_segment", "crescent"],
    "cavity (straight)": ["u_shape", "l_shape", "t_shape", "s_shape"],
    "arms and hooks": ["plus", "hooked_cross", "star"],
}


def make(name: str, **params) -> Polygon:
    """Build shape ``name`` with ``params``; raises KeyError for unknown names."""
    if name not in SHAPES:
        raise KeyError(f"unknown shape '{name}'. Known: {', '.join(sorted(SHAPES))}")
    shape = SHAPES[name](**params)
    if not shape.is_valid or shape.is_empty:
        raise ValueError(f"shape '{name}' with {params} is not a valid polygon")
    return shape
