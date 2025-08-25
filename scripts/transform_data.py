import os
import pandas as pd

# Base directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Input from ingest_data.py output
processed_data_folder = os.path.join(base_dir, "processed_data")

# Output folder to transformed data
transformed_data_folder = os.path.join(base_dir, "transformed_data")
os.makedirs(transformed_data_folder, exist_ok=True)

# List all CSV files in the processed data folder
files = os.listdir(processed_data_folder)
print("Files in processed data folder:", files)

for file_name in files:
    if file_name.endswith(".csv"):
        file_path = os.path.join(processed_data_folder, file_name)
        df = pd.read_csv(file_path)

        # Data transformation
        if 'age' in df.columns:
            df['age_group'] = pd.cut(df['age'], bins=[0, 18, 35, 60, 100], labels=['Child', 'Adult', "Middle Age", 'Senior'])

        if 'name' in df.columns:
            df['name_length'] = df['name'].str.len()

        if 'email' in df.columns:
            df['email_domain'] = df['email'].str.split('@').str[1]

        transformed_path = os.path.join(transformed_data_folder, file_name)
        df.to_csv(transformed_path, index=False)

        print(f"\nTransformed {file_name} saved to {transformed_path}")
        print(df.head())