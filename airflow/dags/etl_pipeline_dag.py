from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

#Define the DAG
with DAG(
    dag_id="etl_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:
    
    ingest = BashOperator(
        task_id="ingest_data",
        bash_command="python /path/to/dataset_pipeline/scripts/ingest_data.py"
    )

    transform = BashOperator(
        task_id="transform_data",
        bash_command="python /path/to/dataset_pipeline/scripts/transform_data.py"
    )

    load = BashOperator(
        task_id="load_data",
        bash_command="python /path/to/dataset_pipeline/scripts/load_to_postgres.py"
    )

    # Define workflow order
    ingest >> transform >> load
