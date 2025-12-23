import os
import psycopg2
import pandas as pd

# Load transformed CSV
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
transformed_data_folder = os.path.join(base_dir, "transformed_data")

# Establish connection to PostgreSQL
conn = psycopg2.connect(
    dbname="etl_project",
    user="airflow",
    password="airflow",
    host="postgres",
    port="5432"
)
cur = conn.cursor()

for file_name in os.listdir(transformed_data_folder):
    if file_name.endswith('.csv'):
        file_path = os.path.join(transformed_data_folder, file_name)
        df = pd.read_csv(file_path)

        for _, row in df.iterrows():
            cur.execute(
                """
                INSERT INTO transformed_data (name, age, email, age_group, name_length, email_domain)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (row['name'], row['age'], row['email'],
                 row.get('age_group'), row.get('name_length'), row.get('email_domain'))
            )

conn.commit()
cur.close()
conn.close()
print("Data loaded successfully into PostgreSQL.")
