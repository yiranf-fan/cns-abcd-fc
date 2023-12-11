#!/bin/bash

if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <sub_folder1> [<sub_folder2> ...]"
    exit 1
fi

derivatives_dir="$SCRATCH/dry_run/derivatives"
output_dir="$SCRATCH/abcd_fc"

# Use an array to store the full paths
full_paths=()

# Loop through all command-line arguments
for sub_folder in "$@"; do
    full_path="${derivatives_dir}/${sub_folder}"
    full_paths+=("$full_path")
done

# Loop through provided sub_folders
for sub_folder in "${full_paths[@]}"; do
    # Check if the provided sub_folder exists
    if [ -d "$sub_folder" ]; then
        # Loop through all 'ses-' folders within the provided 'sub-' folder
        ses_folders=$(find "$sub_folder" -type d -name 'ses-*')
        
        for ses_folder in $ses_folders; do
            # Check if 'func' directory exists within the 'ses-' subdirectory
            func_dir="${ses_folder}/func"
            if [ -d "$func_dir" ]; then
                # Change into the 'func' directory
                cd "$func_dir" || exit

                # Find files with '_space-MNI152NLin2009cAsym_desc-preproc' in their filenames and rename
                find . -type f -name '*_space-MNI152NLin2009cAsym_desc-preproc*' -exec sh -c 'mv "$1" "$(echo "$1" | sed "s/_space-MNI152NLin2009cAsym//")"' sh {} \;

                # Change back to the original directory
                cd - || exit
            fi
        done
        
        # Extract the subject name from the sub_folder path
        subject_name=$(basename "$sub_folder")

        # Create a new directory in the output directory
        new_folder="$output_dir/$subject_name"
        mkdir -p "$new_folder"
        echo "Folder for subject '$subject_name' created at '$output_dir'."
        
    else
        echo "Subfolder '$sub_folder' not found."
    fi
done

