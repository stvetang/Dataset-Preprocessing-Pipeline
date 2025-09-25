from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# Define default arguments for all tasks
default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 1, 1),
    "retries": 1,
}

# DAG definition
with DAG(
    dag_id="etl_pipeline",
    default_args=default_args,
    description="ETL pipeline with transformation and PostgreSQL load",
    schedule_interval=None, #Manual trigger
    catchup=False,
) as dag:
    
    transform = BashOperator(
        task_id="transform_data",
        bash_command="python ./scripts/transform_data.py"
    )

    load_task = BashOperator(
        task_id="load_to_postgres",
        bash_command="python ./scripts/load_to_postgres.py"
    )

    transform >> load_task