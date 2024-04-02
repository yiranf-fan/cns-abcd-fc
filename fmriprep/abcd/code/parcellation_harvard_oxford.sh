#!/bin/bash
#
#SBATCH --job-name=parcellation
#
#SBATCH --output=parcellation_%j.out
#SBATCH --error=parcellation_%j.err
#SBATCH --time=12:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH -p normal
#SBATCH --mail-type=ALL

ml load python/3.9.0
source /scratch/users/yiranf/nilearn/bin/activate
python3 /scratch/groups/kpohl/fmriprep/abcd/code/parcellation_harvard_oxford.py /scratch/groups/kpohl/fmriprep/abcd/code/sub.txt
