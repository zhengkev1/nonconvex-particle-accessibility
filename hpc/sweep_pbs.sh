#!/bin/bash
# PBS job script for a batch accessibility sweep on a cluster.
# Submit with:  qsub -v CONFIG=configs/all_shapes.json hpc/sweep_pbs.sh
#PBS -N accessibility_sweep
#PBS -l nodes=1:ppn=16
#PBS -l walltime=04:00:00
#PBS -j oe

cd "$PBS_O_WORKDIR"
CONFIG=${CONFIG:-configs/all_shapes.json}
NPROCS=$(wc -l < "$PBS_NODEFILE")
echo "Running $CONFIG on $NPROCS ranks"

# Results are appended per job, so resubmitting the same config resumes it.
mpirun -machinefile "$PBS_NODEFILE" -np "$NPROCS" \
    python -m accessibility.sweep "$CONFIG" --mpi
