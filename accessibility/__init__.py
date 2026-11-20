"""Accessibility analysis for non-convex 2D particles."""
from .core import Grid, Result, compute
from .shapes import FAMILIES, SHAPES, make

__all__ = ["Grid", "Result", "compute", "make", "SHAPES", "FAMILIES"]
