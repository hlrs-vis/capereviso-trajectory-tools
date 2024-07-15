#!/bin/bash

# Script to process large amounts of capereviso json-files into bcrtf-files

# List of machines in your cluster
machines=("viscluster50" "viscluster51" "viscluster52" "viscluster53" "viscluster54" "viscluster55" "viscluster56" "viscluster57" "viscluster58" "viscluster59" "viscluster60" "viscluster70" "viscluster71" "viscluster72" "viscluster73" "viscluster74" "viscluster75" "viscluster76" "viscluster77" "viscluster78" "viscluster79" "viscluster80")

# Program directory
program_directory="/mnt/raid/soft/CapeReviso/multi-object-multi-camera-tracker"

# Configuration file
config_file="/data/CapeReviso/visagx_calibrations/vhs-calibration/config_vhs_wg_noshow_m.ini"

# Command to process a file
process_command="python sort_create_bcrtf.py --config $config_file"

# Directory containing the files to be processed
input_directory="/data/CapeReviso/CapeReviso/Herrenberg-Kameradaten2/visagx2-vhs-2023-06-06/cameradata/json/"

# Directory to store processed files
output_directory="/data/CapeReviso/CapeReviso/Herrenberg-Kameradaten2/visagx2-vhs-2023-06-06/cameradata/processed/"

# Function to process a file on a remote machine
process_file() {
    local machine=$1
    local file=$2
    # Move the file first
    ssh $machine "cd $program_directory && workon multi-camera2 && mv $input_directory/$file $output_directory/ && $process_command $output_directory/$file" &
}

files=$(ls $input_directory | grep .gz)

while [ ! -z "$files" ]; do
    # Iterate over each machine in the cluster
    for machine in "${machines[@]}"; do
        #process the first file in the list
        process_file $machine ${files[0]}
        sleep 10
        files=$(ls $input_directory | grep .gz)
    done
done

# Wait for all background tasks to finish
wait
