import os
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder

transformed_data_folder = "/opt/airflow/dags/transformed_data"
anomaly_data_folder = "/opt/airflow/dags/anomaly_data"
os.makedirs(anomaly_data_folder, exist_ok=True)

files = os.listdir(transformed_data_folder)
print("Files in transformed data folder:", files)

for file_name in files:
    if not file_name.endswith(".csv"):
        continue

    file_path = os.path.join(transformed_data_folder, file_name)
    df = pd.read_csv(file_path)

    features = pd.DataFrame()

    if 'age' in df.columns:
        features['age'] = df['age'].fillna(df['age'].mean())

    if 'name_length' in df.columns:
        features['name_length'] = df['name_length'].fillna(0)

    if 'email_domain' in df.columns:
        # LabelEncoder to convert email domains to numeric values
        le = LabelEncoder()
        features['email_domain_encoded'] = le.fit_transform(df['email_domain'].fillna('unknown'))

    if features.empty:
        print(f"Skipping {file_name} as no usable features were found.")
        continue

    # Default to 10% anomalies for now, can be adjusted based on the dataset
    model = IsolationForest(contamination=0.1, random_state=42)
    predictions = model.fit_predict(features) 

    # Returns float value for each row
    scores = model.decision_function(features)

    df['is_anomaly'] = predictions == -1
    df['anomaly_score'] = scores.round(4)

    # Save dataframe with anomalies to anomaly_data folder
    output_path = os.path.join(anomaly_data_folder, file_name)
    df.to_csv(output_path, index=False)

    # Sum all anomalies in the array and print the results
    anomaly_count = df['is_anomaly'].sum()
    print(f"\nProcessed {file_name}: {anomaly_count} anomalies found out of {len(df)} records")
    print(df[['name', 'age', 'email_domain', 'is_anomaly', 'anomaly_score']].head(10))