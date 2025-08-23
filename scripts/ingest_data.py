import os
import pandas as pd

# Define the path to the raw data folder
raw_data_folder = "/dataset_pipeline/raw_data"

# List all CSV files in the raw data folder
files = os.listdir(raw_data_folder)
print("Files in raw data folder:", files)

#Loop through files and load CSVs
for file_name in files:
    if file_name.endswith(".csv"):
        file_path = os.path.join(raw_data_folder, file_name)
        df = pd.read_csv(file_path)
        print(f"\nFirst 5 rows of {file_name}:")
        print(df.head())

