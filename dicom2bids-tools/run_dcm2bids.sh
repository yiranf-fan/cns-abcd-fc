#!/bin/bash

# Define the source directory where raw abcd packages are located
source_dir="$SCRATCH/dicom2bids-tools/abcd/sourcedata/abcd_package_1222190"

# Define the final destination directory where processed bids format are located for fmriprep
destination_dir="$SCRATCH/fmriprep/abcd"

# Define the intermediate directory where dcm2bids convert anatomical dicom files to nifti
intermediate_dir="$SCRATCH/dicom2bids-tools/abcd"

# Move functional tgz files to the destination directory
mv "${source_dir}/fmriresults01/abcd-mproc-release5"/*.tgz "${destination_dir}"

# Untar functional files and remove .tsv file
cd "${destination_dir}"
for tgz_file in *.tgz; do
    if [ -f "$tgz_file" ]; then
        tar -xzf "$tgz_file"
        echo "Untarred ${tgz_file}"
        # Remove the original tgz file
        rm "$tgz_file"
        echo "Deleted ${tgz_file}"
    fi
done

find "${destination_dir}" -type f -name '*.tsv' \
  -not -path '*/derivatives/*' \
  -not -path '*/code/*' \
  -delete

# Back to source directory and untar all the anatomical files
cd "${source_dir}/image03"
for tgz_file in *.tgz; do
    if [ -f "$tgz_file" ]; then
        tar -xzf "$tgz_file"
        echo "Untarred ${tgz_file}"
        # Remove the original tgz file
        rm "$tgz_file"
        echo "Deleted ${tgz_file}"
    fi
done

# Run dcm2bids on anatomical files for all subjects in source directory 
cd "${intermediate_dir}"

# Load dcm2bids tool
ml load python/3.9.0
source $SCRATCH/dicom2bids-tools/dcm2bids/bin/activate

# Convert
config_file="${intermediate_dir}/code/abcd_config.json"
for folder in "${source_dir}/image03"/sub-*; do
    if [ -d "$folder" ]; then
        subject_id=$(basename "$folder")
        echo "Processing ${subject_id}..."
        # Run the command for each folder
        dcm2bids -d "${folder}" -p "${subject_id}" -c "${config_file}" --auto_extract_entities
        echo "Processing complete for ${subject_id}"
        echo "---"
        rm -r "$folder"
        echo "Removed ${subject_id}"
    fi
done


# Organize the anatomical files and functional files to the corresponding folder in destination directory
for subject_dir in "${intermediate_dir}"/sub-*/; do
    if [ -d "$subject_dir" ]; then
        # Extract subject from the subdirectory
        subject=$(basename "$subject_dir")

        # Loop through anat directories within the subject directory
        for file in "${subject_dir}"/anat/*_T1w.json "${subject_dir}"/anat/*_T1w.nii.gz; do
            if [ -f "$file" ]; then
            # Extract subject and session from the filename
            filename=$(basename "$file")
            subject=$(echo "$filename" | awk -F'_' '{print $1}')
            session=$(echo "$filename" | awk -F'_' '{print $2}')

            # Create 'anat' directory in the corresponding subject/session directory
            dest_anat_dir="${destination_dir}/${subject}/${session}/anat"
            mkdir -p "${dest_anat_dir}"

            # Move the file to the 'anat' directory in the destination
            mv "$file" "${dest_anat_dir}/"

            echo "Organization complete for ${subject_id}/${session}"

            fi
        done
        
        rm -r "$subject_dir"
        echo "Rmoved ${subject_dir}"
    fi
done

rm -r "${source_dir}"
