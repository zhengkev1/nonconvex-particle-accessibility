"""Tests: shape library, the accessibility calculation and the batch sweep.

The reproduction tests check the refactored code against values saved by the
original research scripts (frame titles in figures/ and the cross data in
results/cross_hook_accessibility.csv).
"""
import json
import math

import pytest

from accessibility import Grid, compute, make
from accessibility.shapes import FAMILIES, SHAPES
from accessibility.sweep import build_jobs, main as sweep_main

COARSE = Grid(domain_radius=2.5, dx=0.4, dtheta_deg=30)


@pytest.mark.parametrize("name", sorted(SHAPES))
def test_every_shape_builds_valid_polygon(name):
    shape = make(name)
    assert shape.is_valid and not shape.is_empty
    assert shape.geom_type == "Polygon"
    minx, miny, maxx, maxy = shape.bounds
    assert max(abs(minx), abs(miny), abs(maxx), abs(maxy)) < 1.7  # fits the default domains


def test_families_cover_all_shapes():
    listed = {s for names in FAMILIES.values() for s in names}
    assert listed == set(SHAPES)


def test_unknown_shape_raises():
    with pytest.raises(KeyError):
        make("triangle_of_doom")


def test_c_shape_area_matches_formula():
    phi = 30.0
    expected = (1 - 0.75 ** 2) * math.pi * (1 - phi / 360)
    assert make("c_shape", mouth_deg=phi).area == pytest.approx(expected, rel=2e-3)


def test_area_bookkeeping_adds_up():
    r = compute(make("c_shape", mouth_deg=40), COARSE)
    total = r.inaccessibility * r.domain_area + r.particle_area + r.accessible_area
    assert total == pytest.approx(r.domain_area)
    assert r.accessibility == pytest.approx(1 - r.inaccessibility)
    assert 0 < r.valid_placements < r.total_placements


def test_convex_disc_has_little_inaccessible_area():
    # Only grid gaps around the disc are unreachable; no cavity exists.
    r = compute(make("disc"), Grid(domain_radius=2.5, dx=0.1, dtheta_deg=90))
    assert r.inaccessibility < 0.03


def test_narrow_mouth_is_less_accessible_than_wide_mouth():
    narrow = compute(make("c_shape", mouth_deg=5), COARSE).inaccessibility
    wide = compute(make("c_shape", mouth_deg=90), COARSE).inaccessibility
    assert narrow > wide


# --- reproduction of the original research outputs (slower: ~5-15 s each) ---

@pytest.mark.slow
@pytest.mark.parametrize("phi, saved_I", [(24, 0.0733), (45, 0.0227)])
def test_reproduces_saved_c_shape_frames(phi, saved_I):
    r = compute(make("c_shape", mouth_deg=phi), Grid(2.5, 0.2, 4))
    assert round(r.inaccessibility, 4) == saved_I


@pytest.mark.slow
@pytest.mark.parametrize("hook, saved", [(0.6, 0.9272), (1.0, 0.88158)])
def test_reproduces_saved_cross_accessibility(hook, saved):
    grid = Grid(3.0, 0.2, 2, grid_start=-3.1, grid_stop=3.1)
    r = compute(make("hooked_cross", hook_len=hook), grid)
    assert r.accessible_fraction == pytest.approx(saved, abs=5e-5)


def test_sweep_writes_csv_and_resumes(tmp_path, capsys):
    cfg = {
        "name": "t",
        "grid": {"domain_radius": 2.5, "dx": 0.5, "dtheta_deg": 45},
        "sweeps": [{"shape": "star", "vary": "points", "values": [4, 5]},
                   {"shape": "u_shape", "vary": "depth", "values": {"start": 0.5, "stop": 1.1, "step": 0.5}}],
    }
    assert len(build_jobs(cfg)) == 4
    path = tmp_path / "cfg.json"
    path.write_text(json.dumps(cfg))
    out = tmp_path / "out.csv"
    sweep_main([str(path), "--out", str(out)])
    assert len(out.read_text().strip().splitlines()) == 5  # header + 4 rows
    sweep_main([str(path), "--out", str(out)])           # second run: nothing new
    assert len(out.read_text().strip().splitlines()) == 5
    assert "0 to run" in capsys.readouterr().out
