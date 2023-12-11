#!/bin/bash
#
#SBATCH --job-name=parcellation
#
#SBATCH --output=%j.out
#SBATCH --error=%j.err
#SBATCH --time=8:00:00
#SBATCH --mem=8G
#SBATCH -p kpohl
#SBATCH --mail-type=FAIL

ml load python/3.9.0
source /scratch/users/yiranf/nilearn/bin/activate
python3 /scratch/users/yiranf/dry_run/code/parcellation.py
