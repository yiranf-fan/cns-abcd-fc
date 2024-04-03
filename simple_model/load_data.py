import os
import numpy as np
import pandas as pd
import pickle

# Function to iterate through subject list and read CSV files
def read_csv_files(subject_list_file, destination_dir):
    # Read subject list from text file
    with open(subject_list_file, 'r') as f:
        subjects = f.read().splitlines()

    data = []
    
    # Iterate through subjects
    for subject in subjects:
        # Generate subject folder name
        subject_folder = 'sub-' + subject.replace('NDAR_', 'NDAR')
        print(subject_folder)
        # Check if subject folder exists
        if os.path.exists(os.path.join(destination_dir, subject_folder)):
            # Find CSV files with specific naming convention
            csv_files = [f for f in os.listdir(os.path.join(destination_dir, subject_folder)) if f.endswith('_concatenate_difumo_corr.csv')]
            
            # Iterate through CSV files
            for csv_file in csv_files:
                # Construct path to CSV file
                csv_path = os.path.join(destination_dir, subject_folder, csv_file)
                
                # Read CSV file into numpy array
                with open(csv_path, 'rb') as csvfile:
                    corr = np.genfromtxt(csvfile, delimiter=',')
                
                # Append numpy array to data list
                data.append(corr)
        else:
            print(f"Folder not found for subject {subject}")
    
    # Convert list of numpy arrays to 3D numpy array
    data_array = np.stack(data)
    
    return data_array

# Function to write data array to pickle file in chunks
def write_pickle_in_chunks(data_list, output_file, chunk_size=200):
    with open(output_file, 'wb') as f:
        for chunk in data_list:
            pickle.dump(chunk, f)

# Load simple sex classification labels
info = pd.read_csv('/home/groups/kpohl/abcd_data/abcd-data-release-5.0/core/abcd-general/abcd_p_demo.csv')
with open('/home/users/yiranf/sub.txt', 'r') as file:
    sub = [line.strip() for line in file]

sex = info[info['src_subject_id'].isin(sub)].drop_duplicates(subset=['src_subject_id'])['demo_sex_v2'].reset_index(drop=True)
sex.replace({1: 0, 2: 1}, inplace=True) # 0 is male, 1 is female
sex.value_counts()

# Load and save connectivity as pkl
subject_list_file = '/home/users/yiranf/sub.txt'  # Path to text file containing subject list
destination_dir = '/scratch/groups/kpohl/fmriprep/abcd_fc'  # Path to destination directory containing subject folders
output_file = 'difumo.pkl'  # Path to output pickle file

data_array = read_csv_files(subject_list_file, destination_dir)
print("Shape of 3D numpy array:", data_array.shape)

write_pickle_in_chunks(data_array, output_file)
print("Data array saved to", output_file)