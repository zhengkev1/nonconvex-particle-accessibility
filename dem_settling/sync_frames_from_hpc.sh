#!/bin/bash


HPC_USER="your_username"
HPC_HOST="your.hpc.host"
HPC_REMOTE_DIR="/home/your_username/bulk/perigrain-lite/out/2d-cross_6"
LOCAL_DEST_DIR="$HOME/summer_research/video"  # change the last from hpc to desired name
PYTHON_SCRIPT="$HOME/summer_research/video/video_rendering.sh"  # remember to change the name in python file
LOCAL_FILE_DIR="$HOME/summer_research/video/2d-cross_6"  # change the last from hpc to desired name

mkdir -p "$LOCAL_DEST_DIR"


echo "Starting rsync from $HPC_USER@$HPC_HOST:$HPC_REMOTE_DIR to $LOCAL_DEST_DIR ..."
rsync -avz --include="*/" --include="*.png" --exclude="*" "$HPC_USER@$HPC_HOST:$HPC_REMOTE_DIR" "$LOCAL_DEST_DIR/"


if [ -f "$PYTHON_SCRIPT" ]; then
    echo "Running Python script: $PYTHON_SCRIPT"
    "$PYTHON_SCRIPT" "${LOCAL_FILE_DIR}"
else
    echo "Python script not found: $PYTHON_SCRIPT"
fi


echo "Done."
