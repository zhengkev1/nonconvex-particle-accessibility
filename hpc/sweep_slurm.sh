#!/bin/bash
# Slurm version of hpc/sweep_pbs.sh.
# Submit with:  sbatch --export=CONFIG=configs/all_shapes.json hpc/sweep_slurm.sh
#SBATCH --job-name=accessibility_sweep
#SBATCH --ntasks=16
#SBATCH --time=04:00:00
#SBATCH --output=sweep_%j.log

CONFIG=${CONFIG:-configs/all_shapes.json}
srun python -m accessibility.sweep "$CONFIG" --mpi
