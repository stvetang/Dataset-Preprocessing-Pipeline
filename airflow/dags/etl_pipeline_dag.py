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
        bash_command="python /opt/airflow/dags/scripts/ingest_data.py"
    )

    transform = BashOperator(
        task_id="transform_data",
        bash_command="python /opt/airflow/dags/scripts/transform_data.py"
    )

    detect_anomalies = BashOperator(
        task_id="detect_anomalies",
        bash_command="python /opt/airflow/dags/scripts/detect_anomalies.py"
    )

    enrich_with_llm = BashOperator(
        task_id="enrich_with_llm",
        bash_command="python /opt/airflow/dags/scripts/enrich_with_llm.py"
    )

    load_postgres = BashOperator(
        task_id="load_to_postgres",
        bash_command="python /opt/airflow/dags/scripts/load_to_postgres.py"
    )

    load_mongodb = BashOperator(
        task_id="load_to_mongodb",
        bash_command="python /opt/airflow/dags/scripts/load_to_mongodb.py"
    )

    # Define workflow order
    ingest >> transform >> detect_anomalies >> enrich_with_llm >> [load_postgres, load_mongodb]
