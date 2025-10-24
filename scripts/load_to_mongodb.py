from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
from pymongo import MongoClient

def load_to_mongodb():
    # Connect to MongoDB inside Docker
    client = MongoClient(host="mongodb", port=27017)
    db = client["dataset_pipeline"]
    collection = db["employees"]

    # Path to dataset
    file_path = "/opt/airflow/dags/data/employees.csv"

    # Read dataset using pandas
    df = pd.read_csv(file_path)

    # Convert DataFrame to list of dicts (MongoDB format)
    records = df.to_dict("records")

    collection.delete_many({})  # Clear existing data

    # Insert data into MongoDB
    collection.insert_many(records)

    print(f"Successfully loaded {len(records)} records into MongoDB.")

    default_args = {
        "owner": "airflow",
        "start_date": datetime(2025, 1, 1),
        "retries": 1,
    }

    with DAG(
        dag_id="load_to_monogdb",
        default_args=default_args,
        schedule_interval=None,
        catchup=False,
    ) as dag:

        load_task =PythonOperator(
            task_id="load_to_mongodb_task",
            python_callable=load_to_mongodb,
        )

        load_task