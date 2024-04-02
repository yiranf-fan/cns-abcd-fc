# ml load python/3.9.0
# source nilearn/bin/activate

import os
import sys
import json
import numpy as np
import nibabel as nb
from nilearn import datasets
from nilearn.maskers import NiftiLabelsMasker
from nilearn.connectome import ConnectivityMeasure
from nilearn import plotting
from nilearn.interfaces.fmriprep import load_confounds


# helper functions
def get_bold_tr(bold_path):
    json_sidecar_path = '{}.json'.format(
        bold_path.split('.nii.gz')[0]
    )
    if os.path.isfile(json_sidecar_path):
        with open(json_sidecar_path, 'r') as jfile:
            jdata = jfile.read()
        t_r = json.loads(jdata)['RepetitionTime']
    else:
        t_r = nb.load(bold_path).header.get_zooms()[-1]
    return round(float(t_r), 5)


def extract_brain_signal(sub, ses, run):

    time_series_list = []
    
    for r in run:
        nifti_name = sub + '_' + ses + '_task-rest_run-0' + str(r) + '_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'
        nifti_path = os.path.join(derivatives_dir, sub, ses, 'func', nifti_name)
        t_r = get_bold_tr(nifti_path)

        masker = NiftiLabelsMasker(
            labels_img=atlas_filename,
            standardize="zscore_sample",
            standardize_confounds="zscore_sample",
            memory="nilearn_cache",
            verbose=5,
            labels=labels,
            resampling_target="labels",
            t_r = t_r,
        )

        masker_sub = NiftiLabelsMasker(
            labels_img=atlas_filename_sub,
            standardize="zscore_sample",
            standardize_confounds="zscore_sample",
            memory="nilearn_cache",
            verbose=5,
            labels=labels_sub,
            t_r=t_r,
        )

        confounds_simple, sample_mask = load_confounds(
            nifti_path,
            strategy=["high_pass", "motion", "wm_csf"],
            motion="basic",
            wm_csf="basic",
        )

        time_series = masker.fit_transform(
            nifti_path, confounds=confounds_simple, sample_mask=sample_mask
        )

        time_series_sub = masker_sub.fit_transform(
            nifti_path, confounds=confounds_simple, sample_mask=sample_mask
        )

        time_series_concat = np.concatenate((time_series, time_series_sub), axis=1)
        time_series_concat = time_series_concat[12:, :]
        time_series_list.append(time_series_concat)
    
    return time_series_list


def compute_time_series(time_series_list, method='concatenate'):

    if method == 'average':
        if len(set(len(ts) for ts in time_series_list)) > 1:
            print('Unable to process averaged time series - dimensions are not the same')
            return None
        else:
            time_series_result = np.mean(time_series_list, axis=0)

    elif method == 'concatenate':
        time_series_result = np.concatenate(time_series_list, axis=0)

    else:
        print('Unrecognized method, please specify average or concatenate')
        sys.exit(1)

    return time_series_result


def compute_correlation(time_series, sub, ses, method='_concatenate'):
    correlation_measure = ConnectivityMeasure(
        kind="correlation",
        standardize="zscore_sample",
    )

    save_path = os.path.join(fc_dir, sub)

    correlation_matrix = correlation_measure.fit_transform([time_series])[0]
    np.fill_diagonal(correlation_matrix, 0)

    plotting.show()
    display = plotting.plot_matrix(
        correlation_matrix,
        figure=(20, 16),
        labels=labels[1:] + labels_sub[1:],
        vmax=0.8,
        vmin=-0.8,
        title="Motion, WM, CSF Confounds Removed FC",
    )

    filename = ses + method + '_ho_corr.png'
    display.figure.savefig(os.path.join(save_path, filename))

    filename = ses + method + '_ho_corr.csv'
    np.savetxt(os.path.join(save_path, filename), correlation_matrix, delimiter=',')


def run_parcellation(sub, ses, run):
    time_series_list = extract_brain_signal(sub, ses, run)
    # SKIPPING AVERAGE NOW
    # ts_avg = compute_time_series(time_series_list, 'average')
    # if ts_avg is not None:
        # compute_correlation(ts_avg, sub, ses, '_average')

    ts_concat = compute_time_series(time_series_list, 'concatenate')
    compute_correlation(ts_concat, sub, ses, '_concatenate')


def main(subject_file):
    with open(subject_file, 'r') as file:
        subjects = [line.strip() for line in file if line.strip()]
    sessions = ['ses-baselineYear1Arm1', 'ses-2YearFollowUpYArm1', 'ses-4YearFollowUpYArm1']

    for sub in subjects:
        subject_dir = os.path.join(derivatives_dir, sub)
        if not os.path.exists(subject_dir):
            print(f"Subject folder '{sub}' does not exist. Skipping...")
            continue

        subject_output_dir = os.path.join(fc_dir, sub)
        os.makedirs(subject_output_dir, exist_ok=True)

        for ses in sessions:
            nifti_folder_path = os.path.join(derivatives_dir, sub, ses, 'func')
            num_files = len([f for f in os.listdir(nifti_folder_path)])

            if num_files % 11 != 0:
                print(f"Number of files ({num_files}) for subject {sub} is not divisible by 11. Skipping this session.")
                continue

            num_runs = num_files // 11
            run = list(range(1, num_runs + 1))

            run_parcellation(sub, ses, run)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 parcellation.py <subjects_file.txt>")
        sys.exit(1)

    subjects_file = sys.argv[1]

    dataset = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm", symmetric_split=True)
    atlas_filename = dataset.maps
    labels = dataset.labels

    dataset_sub = datasets.fetch_atlas_harvard_oxford("sub-maxprob-thr25-2mm", symmetric_split=False)
    atlas_filename_sub = dataset_sub.maps
    labels_sub = dataset_sub.labels

    derivatives_dir = '/scratch/groups/kpohl/fmriprep/abcd/derivatives'
    fc_dir = '/scratch/groups/kpohl/fmriprep/abcd_fc'

    main(subjects_file)

# how to reload the correlation matrix
# corr = np.genfromtxt(save_path, delimiter=',')