import os
import pandas as pd

# Base directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define the path to the raw data folder
raw_data_folder = os.path.join(base_dir, "raw_data")

processed_data_folder = os.path.join(base_dir, "processed_data")

# List all CSV files in the raw data folder
files = os.listdir(raw_data_folder)
print("Files in raw data folder:", files)

#Loop through files and load CSVs
for file_name in files:
    if file_name.endswith(".csv"):
        file_path = os.path.join(raw_data_folder, file_name)
        df = pd.read_csv(file_path)

        # Data cleaning
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        df = df.drop_duplicates()

        if 'age' in df.columns:
            mean_age = df['age'].mean()
            df['age'] = df['age'].fillna(mean_age)
        
        if 'name' in df.columns:
            df['name'] = df['name'].str.title()

        if 'email' in df.columns:
            df['email'] = df['email'].str.lower()

        processed_path = os.path.join(processed_data_folder, file_name)
        df.to_csv(processed_path, index=False)

        print(f"\nProcessed {file_name} saved to {processed_path}")
        print(df.head())
