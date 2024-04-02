#!/bin/bash
#
#SBATCH --job-name=parcellation_1
#
#SBATCH --output=parcellation_1_%j.out
#SBATCH --error=parcellation_1_%j.err
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH -p normal
#SBATCH --mail-type=ALL

ml load python/3.9.0
source /scratch/users/yiranf/lfb/bin/activate
python3 /scratch/groups/kpohl/fmriprep/abcd/code/parcellation_difumo.py /scratch/groups/kpohl/fmriprep/abcd/code/sub_1.txt
