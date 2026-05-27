import os
import psycopg2
import pandas as pd

# Load transformed CSV
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
enriched_data_folder = os.path.join(base_dir, "enriched_data")

# Establish connection to PostgreSQL
conn = psycopg2.connect(
    dbname="etl_project",
    user="airflow",
    password="airflow",
    host="postgres",
    port="5432"
)
cur = conn.cursor()

for file_name in os.listdir(enriched_data_folder):
    if not file_name.endswith('.csv'):
        continue

    file_path = os.path.join(enriched_data_folder, file_name)
    df = pd.read_csv(file_path)

    for _, row in df.iterrows():
        cur.execute(
            """
            INSERT INTO transformed_data (
                name, age, email, age_group, name_length, email_domain, 
                is_anomaly, anomaly_score, predicted_category, data_quality_notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                row.get('name'), 
                row.get('age'), 
                row.get('email'),
                row.get('age_group'), 
                row.get('name_length'), 
                row.get('email_domain'),
                row.get('is_anomaly'),            # Boolean value
                row.get('anomaly_score'),         # Float value
                row.get('predicted_category'), 
                row.get('data_quality_notes')
            )
        )

conn.commit()
cur.close()
conn.close()
print("Data loaded successfully into PostgreSQL.")
