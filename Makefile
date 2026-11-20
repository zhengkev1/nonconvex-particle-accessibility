# Common tasks. Run from the repository root after `pip install -e .`
WORKERS ?= 4

.PHONY: install test test-all reproduce shapes compare convergence figures all

install:
	pip install -e ".[test]"

test:            ## fast tests (a few seconds)
	python -m pytest -q -m "not slow"

test-all:        ## includes reproduction of saved research outputs (~1 min)
	python -m pytest -q

reproduce:       ## recompute the original C-shape and cross sweeps
	python -m accessibility.sweep configs/reproduce_c_shape.json --workers $(WORKERS)
	python -m accessibility.sweep configs/reproduce_cross.json --workers $(WORKERS)

shapes:          ## batch sweep over every shape family
	python -m accessibility.sweep configs/all_shapes.json --workers $(WORKERS)

compare: shapes
	python analysis/compare_shapes.py results/all_shapes.csv

convergence:
	python analysis/grid_convergence.py

figures:
	python shapes/shape_gallery.py
	python analysis/summary_plots.py
	python analysis/compare_shapes.py results/all_shapes.csv

all: test reproduce shapes figures
