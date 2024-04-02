#!/bin/bash
#
#SBATCH --job-name=fmriprep_NDARINV9D91PDLZ
#
#SBATCH --output=fmriprep_%j.out
#SBATCH --error=fmriprep_%j.err
#SBATCH --time=12:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH -p normal
#SBATCH --mail-type=ALL

export FS_LICENSE=/scratch/groups/kpohl/fmriprep/abcd/derivatives/license.txt
bids_root_dir=/scratch/groups/kpohl/fmriprep/abcd
nthreads=4

subjects=("sub-NDARINV9D91PDLZ")

for subj in "${subjects[@]}"; do
    singularity run --cleanenv $HOME/fmriprep/fmriprep-23.1.3.simg $bids_root_dir $bids_root_dir/derivatives participant --participant-label $subj -w /scratch/groups/kpohl/fmriprep/work --dummy-scans 6 --md-only-boilerplate --fs-license-file /scratch/groups/kpohl/fmriprep/abcd/derivatives/license.txt --fs-no-reconall --nthreads $nthreads --stop-on-first-crash
    subj_id="${subj:4}"
    rm -r /scratch/groups/kpohl/fmriprep/work/fmriprep_23_1_wf/single_subject_"$subj_id"_wf
done