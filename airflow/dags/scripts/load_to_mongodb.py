import os
import pandas as pd
from pymongo import MongoClient

client = MongoClient(host="mongodb", port=27017)
db = client["dataset_pipeline"]
collection = db["employees"]

enriched_data_folder = "/opt/airflow/dags/enriched_data"

# Clear any existing data in the collection
collection.delete_many({})      

for file_name in os.listdir(enriched_data_folder):
    if not file_name.endswith(".csv"):
        continue

    file_path = os.path.join(enriched_data_folder, file_name)
    df = pd.read_csv(file_path)

    records = df.to_dict("records")
    collection.insert_many(records)

    print(f"Successfully loaded {len(records)} records from {file_name} into MongoDB.")