# ml load python/3.9.0
# source nilearn/bin/activate

import os
import sys
import numpy as np
from nilearn import datasets
from nilearn.maskers import NiftiLabelsMasker
from nilearn.connectome import ConnectivityMeasure
from nilearn import plotting
from nilearn.interfaces.fmriprep import load_confounds


dataset = datasets.fetch_atlas_harvard_oxford("cort-maxprob-thr25-2mm", symmetric_split=True)
atlas_filename = dataset.maps
labels = dataset.labels

masker = NiftiLabelsMasker(
    labels_img=atlas_filename,
    standardize="zscore_sample",
    standardize_confounds="zscore_sample",
    memory="nilearn_cache",
    verbose=5,
    labels=labels,
    resampling_target="labels",
)

dataset_sub = datasets.fetch_atlas_harvard_oxford("sub-maxprob-thr25-2mm", symmetric_split=False)
atlas_filename_sub = dataset_sub.maps
labels_sub = dataset_sub.labels

masker_sub = NiftiLabelsMasker(
    labels_img=atlas_filename_sub,
    standardize="zscore_sample",
    standardize_confounds="zscore_sample",
    memory="nilearn_cache",
    verbose=5,
    labels=labels_sub,
)

correlation_measure = ConnectivityMeasure(
    kind="correlation",
    standardize="zscore_sample",
)

derivatives_dir = '/scratch/users/yiranf/dry_run/derivatives/'
fc_dir = '/scratch/users/yiranf/abcd_fc/'

def extract_brain_signal(sub, ses):
    if sub == 'sub-NDARINV1JXDFV9Z' and ses == 'ses-baselineYear1Arm1':
        run = [1, 2, 3]
    elif sub == 'sub-NDARINV10HWA6YU' and ses == 'ses-4YearFollowUpYArm1':
        run = [1, 2, 3]
    elif sub == 'sub-NDARINV0CF1U8X8' and ses == 'ses-baselineYear1Arm1':
        run = [1, 2, 3]
    else:
        run = [1, 2, 3, 4]

    # run = [1, 2, 3, 4]

    time_series_list = []
    
    for r in run:
        nifti_path = derivatives_dir + sub + '/' + ses + '/func/' + sub + '_' + ses + '_task-rest_run-0' + str(
            r) + '_desc-preproc_bold.nii.gz'
        # nifti_path = '/scratch/users/yiranf/dry_run/derivatives/sub-NDARINVF7UTX830/ses-baselineYear1Arm1/func/
        # sub-NDARINVF7UTX830_ses-baselineYear1Arm1_task-rest_run-01_desc-preproc_bold.nii.gz'

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
        time_series_concat = time_series_concat[6:, :]
        time_series_list.append(time_series_concat)
    
    return time_series_list


def compute_time_series(time_series_list, method='average'): 

    if method == 'average':
        time_series_result = np.mean(time_series_list, axis=0)

    elif method == 'concatenate':
        time_series_result = np.concatenate(time_series_list, axis=0)

    else:
        print('Unrecognized method, please specify average or concatenate')
        sys.exit(1)

    return time_series_result


def compute_correlation(time_series, sub, ses, method='_average'):
    save_path = fc_dir + sub + '/'
    # save_path = '/scratch/users/yiranf/abcd_fc/sub-NDARINVF7UTX830/'

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
        reorder=True,
    )

    filename = ses + method + '_corr.png'
    # filename = 'ses-baselineYear1Arm1_average_corr.png'
    display.figure.savefig(os.path.join(save_path, filename))

    filename = ses + method + '_corr.csv'
    # filename = 'ses-baselineYear1Arm1_average_corr.csv'
    np.savetxt(os.path.join(save_path, filename), correlation_matrix, delimiter=',')


subjects = ['sub-NDARINV1JXDFV9Z', 'sub-NDARINV1DDX454E', 'sub-NDARINV1H63RRB3', 'sub-NDARINV10HWA6YU', 'sub-NDARINV0CF1U8X8']
sessions = ['ses-baselineYear1Arm1', 'ses-2YearFollowUpYArm1', 'ses-4YearFollowUpYArm1']

for sub in subjects:
    for ses in sessions:
        ts_list = extract_brain_signal(sub, ses)
        ts_avg = compute_time_series(ts_list, 'average')
        compute_correlation(ts_avg, sub, ses, '_average')

        ts_concat = compute_time_series(ts_list, 'concatenate')
        compute_correlation(ts_concat, sub, ses, '_concatenate')


# how to reload the correlation matrix
# corr = np.genfromtxt(save_path, delimiter=',')