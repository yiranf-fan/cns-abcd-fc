Update as of Dec. 10, 2023

The following documentation specifies how to obtain fine-grained functional connectivity matrices from ABCD raw data release. Details see [this document](https://docs.google.com/document/d/1PunG-5gJTUv9EBZxjpVr8JhUf0b75d3eumAUpzWW6s0/edit?usp=sharing).

Working directories:
- ./dicom2bids-tools/: directory containing software and script to run the conversion from DICOM to NIFTI for raw data
    - /abcd/: BIDS-compliant directory that contains code necessary to run dcm2bids and source data to work with
        * /code/: abcd_config.json - configuration file required for dcm2bids to have sidecar pairing
        * /sourcedata/: where the raw data package should be located at
    - /dcm2bids/: virtual environment for dcm2bids to run
    - run_dcm2bids.sh: shell script to part 1 of the pipeline (see below)
- ./fmriprep/: directory containing software and scripts to preprocess BIDS-compliant ABCD data using fMRI Prep
    - /abcd/: BIDS-compliant folder that contains organized pre- and post-processed imaging data
        * /code/: contains SLURM script to submit fMRI prep/parcellation jobs, script for arrange functional connectivity map output, and parcellation script
        * /derivatives/: contains all output of fMRI prep organized in BIDS format
            * license.txt: FreeSurfer license
    - /work/: working directory for fMRI prep pipeline
- within_between_similarity.py: initial analysis script for functional connectivity maps


Softwares to install: \
[fMRI Prep](https://fmriprep.org/en/23.1.3/index.html)\
[dcm2bids](https://unfmontreal.github.io/Dcm2Bids/3.1.1/)\
[Nilearn](https://nilearn.github.io/stable/index.html) \
