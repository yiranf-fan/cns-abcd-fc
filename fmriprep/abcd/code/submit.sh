#!/bin/bash
#
#SBATCH --job-name=fmriprep
#
#SBATCH --output=fmriprep_test.%j.out
#SBATCH --error=fmriprep_test.%j.err
#SBATCH --time=9:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH -p kpohl
#SBATCH --mail-type=FAIL

bids_root_dir=$SCRATCH/fmriprep/abcd
subj=sub-NDARINV1JXDFV9Z
nthreads=4

export FS_LICENSE=$SCRATCH/fmriprep/abcd/derivatives/license.txt

singularity run --cleanenv $HOME/fmriprep-23.1.3.simg $bids_root_dir $bids_root_dir/derivatives participant --participant-label $subj \
-w $SCRATCH/fmriprep/work --dummy-scans 6 --md-only-boilerplate --fs-license-file $SCRATCH/fmriprep/abcd/derivatives/license.txt \
--fs-no-reconall --nthreads $nthreads --stop-on-first-crash

