#!/bin/bash

# Unfinished script to process bcrtf-files with read_trajectories.py

# List of machines in your cluster
machines=("viscluster50" "viscluster51" "viscluster52" "viscluster53" "viscluster54" "viscluster55" "viscluster56" "viscluster57" "viscluster58" "viscluster59" "viscluster60" "viscluster70" "viscluster71" "viscluster72" "viscluster73" "viscluster74" "viscluster75" "viscluster76" "viscluster77" "viscluster78" "viscluster79" "viscluster80")

# Program directory
program_directory="/mnt/raid/soft/CapeReviso/multi-object-multi-camera-tracker"

# Configuration file
config_file="/data/CapeReviso/visagx_calibrations/vhs-calibration/config_vhs_wg_noshow_m.ini"

# Command to process a file
process_command="python read_trajectories.py --config $config_file"

# Directory containing the files to be processed
input_directory="/data/CapeReviso/CapeReviso/Herrenberg-Kameradaten2/visagx2-vhs-2023-06-06/cameradata/bcrtf/"

output_directory="/data/CapeReviso/CapeReviso/Herrenberg-Kameradaten2/visagx2-vhs-2023-06-06/cameradata/bcrtf/processed"

# Function to process a file on a remote machine
process_file() {
    local machine=$1
    local file=$2
    # Move the file first
    echo ssh $machine "cd $program_directory && workon multi-camera2 && $process_command $input_directory/$file" &
    ssh $machine "cd $program_directory && workon multi-camera2 && mv $input_directory/$file $output_directory/ && $process_command $output_directory/$file" &
}

for file in "$input_directory"/*bcrtf*; do
    first_file=$(basename "$file")
    break
done


while [ ! -z "$first_file" ]; do
    # Iterate over each machine in the cluster
    for machine in "${machines[@]}"; do
        #process the first file in the list
        process_file $machine $first_file
        first_file=""
        sleep 10
        for file in "$input_directory"/*bcrtf*; do
            first_file=$(basename "$file")
            break
        done
    done
done

# Wait for all background tasks to finish
wait
