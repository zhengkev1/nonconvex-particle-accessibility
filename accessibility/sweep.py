"""Batch accessibility sweeps driven by a JSON config.

A config lists the grid and one or more shape sweeps:

    {
      "name": "c_shape_mouth",
      "grid": {"domain_radius": 2.5, "dx": 0.2, "dtheta_deg": 4},
      "sweeps": [
        {"shape": "c_shape", "vary": "mouth_deg", "values": [0, 5, 10],
         "fixed": {"inner_radius": 0.75}}
      ]
    }

``values`` can also be a range: {"start": 0, "stop": 95, "step": 5}.

Each (shape, parameter value) is one independent job. Jobs run serially, in a
local process pool (--workers N) or across MPI ranks (--mpi, launched with
mpirun). Results are appended to results/<name>.csv one row per job, so an
interrupted sweep resumes where it stopped. --frames saves a picture of the
accessible region for every job.

Usage:
    python -m accessibility.sweep configs/c_shape_mouth.json --workers 4
    mpirun -n 16 python -m accessibility.sweep configs/all_shapes.json --mpi
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np

from .core import Grid, compute
from .shapes import make

FIELDS = ["shape", "param", "value", "params_json", "inaccessibility", "accessibility",
          "accessible_fraction", "accessible_area", "particle_area", "domain_area",
          "valid_placements", "total_placements", "seconds", "grid_json"]


def expand_values(values) -> list:
    if isinstance(values, dict):
        vals = np.arange(values["start"], values["stop"], values["step"])
        return [round(float(v), 10) for v in vals]
    return list(values)


def build_jobs(config: dict) -> list[dict]:
    jobs = []
    for sw in config["sweeps"]:
        fixed = sw.get("fixed", {})
        for v in expand_values(sw["values"]):
            params = dict(fixed, **{sw["vary"]: v})
            jobs.append({"shape": sw["shape"], "param": sw["vary"], "value": v, "params": params})
    return jobs


def job_key(shape: str, params: dict) -> str:
    return shape + "|" + json.dumps(params, sort_keys=True)


def done_keys(csv_path: Path) -> set:
    if not csv_path.exists():
        return set()
    with open(csv_path, newline="") as f:
        return {r["shape"] + "|" + r["params_json"] for r in csv.DictReader(f)}


def run_job(job: dict, grid: Grid, frames_dir: str | None = None) -> dict:
    shape = make(job["shape"], **job["params"])
    if frames_dir:
        res, region = compute(shape, grid, return_region=True)
        save_frame(shape, region, grid, job, res, frames_dir)
    else:
        res = compute(shape, grid)
    row = {
        "shape": job["shape"],
        "param": job["param"],
        "value": job["value"],
        "params_json": json.dumps(job["params"], sort_keys=True),
        "grid_json": json.dumps(asdict(grid), sort_keys=True),
    }
    row.update(res.as_dict())
    return row


def save_frame(shape, region, grid: Grid, job: dict, res, frames_dir: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from .plotting import draw

    r = grid.domain_radius
    fig, ax = plt.subplots(figsize=(5, 5))
    draw(ax, region, "#2f9e44", alpha=0.4)
    draw(ax, shape, "#4c6ef5", alpha=0.8)
    ax.set_title(f"{job['shape']}  {job['param']} = {job['value']:g}   I = {res.inaccessibility:.4f}")
    ax.set_xlim(-r, r)
    ax.set_ylim(-r, r)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    os.makedirs(frames_dir, exist_ok=True)
    fig.savefig(f"{frames_dir}/{job['shape']}_{job['param']}_{job['value']:08.3f}.png", dpi=110)
    plt.close(fig)


def append_rows(csv_path: Path, rows: list[dict]) -> None:
    new = not csv_path.exists()
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in FIELDS})


def _worker(args):
    job, grid, frames_dir = args
    return run_job(job, grid, frames_dir)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("config", help="JSON sweep config")
    ap.add_argument("--out", default=None, help="output CSV (default results/<name>.csv)")
    ap.add_argument("--workers", type=int, default=1, help="local processes (default 1)")
    ap.add_argument("--mpi", action="store_true", help="split jobs across MPI ranks")
    ap.add_argument("--frames", default=None, help="folder for one PNG per job")
    ap.add_argument("--dry-run", action="store_true", help="list jobs and exit")
    a = ap.parse_args(argv)

    config = json.loads(Path(a.config).read_text())
    grid = Grid(**config.get("grid", {}))
    out = Path(a.out or f"results/{config['name']}.csv")
    jobs = build_jobs(config)
    done = done_keys(out)
    todo = [j for j in jobs if job_key(j["shape"], j["params"]) not in done]

    rank, size, comm = 0, 1, None
    if a.mpi:
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        rank, size = comm.Get_rank(), comm.Get_size()

    if rank == 0:
        print(f"{config['name']}: {len(jobs)} jobs, {len(jobs) - len(todo)} already in {out}, "
              f"{len(todo)} to run on {size if a.mpi else a.workers} worker(s) "
              f"[{platform.node()}, python {sys.version.split()[0]}]", flush=True)
    if a.dry_run:
        for j in todo:
            print(" ", j["shape"], j["params"])
        return 0

    if a.mpi:
        mine = todo[rank::size]
        rows = []
        for j in mine:
            rows.append(run_job(j, grid, a.frames))
            print(f"[rank {rank}] {j['shape']} {j['param']}={j['value']:g} "
                  f"I={rows[-1]['inaccessibility']:.5f} ({rows[-1]['seconds']:.1f}s)", flush=True)
        gathered = comm.gather(rows, root=0)
        if rank == 0:
            append_rows(out, [r for part in gathered for r in part])
    elif a.workers > 1:
        from multiprocessing import Pool
        with Pool(a.workers) as pool:
            for row in pool.imap_unordered(_worker, [(j, grid, a.frames) for j in todo]):
                append_rows(out, [row])  # write as results arrive, so a crash loses little
                print(f"{row['shape']} {row['param']}={row['value']:g} "
                      f"I={row['inaccessibility']:.5f} ({row['seconds']:.1f}s)", flush=True)
    else:
        for j in todo:
            row = run_job(j, grid, a.frames)
            append_rows(out, [row])
            print(f"{row['shape']} {row['param']}={row['value']:g} "
                  f"I={row['inaccessibility']:.5f} ({row['seconds']:.1f}s)", flush=True)

    if rank == 0:
        print(f"done -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
