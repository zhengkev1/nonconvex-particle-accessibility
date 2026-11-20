"""Cross-with-hooks particle shapes for 2D DEM settling runs in perigrain.

These two functions were added to perigrain-lite's shape_dict.py so the same
cross shape used in cross_shape/cross_hook_sweep.py could be meshed and settled
in the peridynamics/DEM code. They rely on perigrain's Shape class,
gen_nonconvex_interceptors and pygmsh, so they run only inside a perigrain-lite
checkout (https://github.com/debdeepbh/perigrain-lite), not on their own.
"""
import numpy as np
import pygmsh
import shapely
from shapely.geometry import Polygon
from shapely.affinity import rotate, translate
from shapely.ops import unary_union

from shape_dict import Shape, gen_nonconvex_interceptors  # perigrain-lite


def cross_shape(bar_len=1.5, bar_thk=0.3,
                            hook_len=0.5, hook_thk=0.3,
                            scaling=1e-3, angle_deg=0):
    """
    Returns a Shape representing a cross with thick bars and rectangular hooks at each end.
    Parameters follow screenshot from Rainnnnn1010/perigrain-lite
    """


    # Half-sizes
    hl = bar_len / 2
    ht = bar_thk / 2
    hl_hook = hook_len / 2
    ht_hook = hook_thk / 2

    # Center bars
    h_bar = Polygon([
        (-hl, -ht), (hl, -ht),
        (hl, ht), (-hl, ht)
    ])
    v_bar = Polygon([
        (-ht, -hl), (ht, -hl),
        (ht, hl), (-ht, hl)
    ])

    # Hooks on each arm (top, bottom, left, right)
    top = Polygon([
        (-hl_hook, hl), (hl_hook, hl),
        (hl_hook, hl + hook_thk), (-hl_hook, hl + hook_thk)
    ])
    bottom = Polygon([
        (-hl_hook, -hl - hook_thk), (hl_hook, -hl - hook_thk),
        (hl_hook, -hl), (-hl_hook, -hl)
    ])
    left = Polygon([
        (-hl - hook_thk, -hl_hook), (-hl, -hl_hook),
        (-hl, hl_hook), (-hl - hook_thk, hl_hook)
    ])
    right = Polygon([
        (hl, -hl_hook), (hl + hook_thk, -hl_hook),
        (hl + hook_thk, hl_hook), (hl, hl_hook)
    ])

    # Combine everything
    full = unary_union([h_bar, v_bar, top, bottom, left, right])

    # Shift to center
    centroid = full.centroid
    full = translate(full, xoff=-centroid.x, yoff=-centroid.y)

    # Rotate
    full = rotate(full, angle_deg, origin=(0, 0), use_radians=False)

    # Extract points
    x, y = full.exterior.coords.xy
    points = np.array([x, y]).T[:-1]  # remove last point
    points = np.flip(points, axis= 0)

    # Apply scaling
    points *= scaling

    with pygmsh.occ.Geometry() as geom:

        polygon1 = geom.add_polygon(
            points,
            mesh_size= 1e-4,
        )
        geom.add_physical(polygon1.surface, "surface1")
        #mesh = geom.generate_mesh()
        #meshio.write('cross.msh', mesh, file_format="gmsh")

    # Add interceptors
    nci = gen_nonconvex_interceptors(points)
    nci.use = 'bisec'

    return Shape(points, nci)


def cross_shape_v2(ratio=0.25, scaling=1e-3, sample_spacing=0.25e-3):
    """
    A cross shape built from four bars + hooks, unified to avoid overlapping sample points.
    """
    long = 1
    short = ratio * long
    hook = ratio * 0.8

    # Build rectangles (bars + hooks)
    parts = []

    # vertical bar
    parts.append(shapely.geometry.box(-short, -long, short, long))
    # horizontal bar
    parts.append(shapely.geometry.box(-long, -short, long, short))

    # hooks
    parts.append(shapely.geometry.box(long - hook, -short, long + hook, short))   # right
    parts.append(shapely.geometry.box(-long - hook, -short, -long + hook, short)) # left
    parts.append(shapely.geometry.box(-short, long - hook, short, long + hook))   # top
    parts.append(shapely.geometry.box(-short, -long - hook, short, -long + hook)) # bottom

    # Union shape and scale
    unioned = unary_union(parts)
    unioned = shapely.affinity.scale(unioned, xfact=scaling, yfact=scaling)

    # Sample points in a grid and keep only inside
    minx, miny, maxx, maxy = unioned.bounds
    xs = np.arange(minx, maxx, sample_spacing)
    ys = np.arange(miny, maxy, sample_spacing)
    X, Y = np.meshgrid(xs, ys)
    points = np.vstack((X.ravel(), Y.ravel())).T

    # Filter: keep only points inside the shape
    mask = np.array([unioned.contains(shapely.geometry.Point(p)) for p in points])
    filtered = points[mask]

    # Interceptors from outer contour
    nonconvex_interceptor = gen_nonconvex_interceptors(np.array(unioned.exterior.coords))
    nonconvex_interceptor.use = 'bisec'

    return Shape(filtered, nonconvex_interceptor)
