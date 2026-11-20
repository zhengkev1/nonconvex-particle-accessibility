"""Small Matplotlib helpers for Shapely geometries."""
from __future__ import annotations


def draw(ax, geom, color, alpha=0.8, edgecolor="black", lw=0.5):
    """Fill a Polygon, MultiPolygon or GeometryCollection, leaving holes white."""
    if geom.is_empty:
        return
    kind = geom.geom_type
    if kind == "Polygon":
        x, y = geom.exterior.xy
        ax.fill(x, y, fc=color, alpha=alpha, ec=edgecolor, lw=lw)
        for ring in geom.interiors:
            xi, yi = ring.xy
            ax.fill(xi, yi, fc="white", ec=edgecolor, lw=lw)
    elif kind in ("MultiPolygon", "GeometryCollection"):
        for g in geom.geoms:
            draw(ax, g, color, alpha, edgecolor, lw)
