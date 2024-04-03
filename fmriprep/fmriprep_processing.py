# Script for batch submitting fmriprep jobs by camgonza

# Open the file using a with statement to ensure it's properly closed after reading
subjects = []
with open('subjects.txt', 'r') as file:
    # Iterate over each line in the file
    for line in file:
        subjects.append(line.strip())
        print(line.strip())
        
for subject_ix, subject in enumerate(subjects):

    shell_script_content = '''#!/bin/bash
#SBATCH --job-name=fmriprep_'''+subject+'''
#SBATCH --output=fmriprep_test.%j.out
#SBATCH --error=fmriprep_test.%j.err
#SBATCH --time=12:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH -p normal
#SBATCH --mail-user=camgonza@stanford.edu
#SBATCH --mail-type=ALL

export FS_LICENSE=/scratch/groups/kpohl/fmriprep/abcd/derivatives/license.txt
bids_root_dir=/scratch/groups/kpohl/fmriprep/abcd
nthreads=4

subjects=("sub-'''+subject+'''")

for subj in "${subjects[@]}"; do
    singularity run --cleanenv $HOME/fmriprep/fmriprep-23.1.3.simg $bids_root_dir $bids_root_dir/derivatives participant --participant-label $subj -w /scratch/groups/kpohl/fmriprep/work --dummy-scans 6 --md-only-boilerplate --fs-license-file /scratch/groups/kpohl/fmriprep/abcd/derivatives/license.txt --fs-no-reconall --nthreads $nthreads --stop-on-first-crash
    subj_id="${subj:4}"
    rm -r /scratch/groups/kpohl/fmriprep/work/fmriprep_23_1_wf/single_subject_"$subj_id"_wf
done'''

    # Path where the shell script will be saved
    shell_script_path = "fmriprep_jobs/submit_"+str(subject_ix)+".sh"

    # Writing the shell script content to the file
    with open(shell_script_path, 'w') as file:
        file.write(shell_script_content)

    # Making the shell script executable
    # This is equivalent to running `chmod +x hello_world.sh` in the terminal
    import os
    os.chmod(shell_script_path, 0o755)  # 0o755 sets the file to be readable and executable by everyone, but only writable by the owner
