# ETL Data Pipeline with Airflow, PostgreSQL, and MongoDB

## Overview

This project is an end-to-end **ETL (Extract, Transform, Load) data pipeline** built in Python and orchestrated with **Apache Airflow**, fully containerized using **Docker**. It ingests raw CSV datasets, performs data cleaning and transformation, and stores the processed results in both **PostgreSQL (SQL)** and **MongoDB (NoSQL)** databases for downstream analysis.

The project began as a simple Python data-processing script and was iteratively expanded into a production-style pipeline with automation, orchestration, containerization, and multiple storage backends.

## Architecture

### Pipeline Flow

```text
Raw CSV Data
   ↓
Ingest (clean & normalize)
   ↓
Transform (feature engineering)
   ↓
Load to PostgreSQL (relational)
   ↓
Load to MongoDB (document-based)
```
---
Technologies Used
* Python
* Apache Airflow
* Docker & Docker Compose
* PostgreSQL
* MongoDB
* pandas
* psycopg2
* pymongo
* Linux-based container environments
---
Project Structure
```
dataset_pipeline/
├── airflow/
│   ├── dags/
│   │   ├── etl_pipeline_dag.py
│   │   ├── load_to_mongodb.py
│   │   └── scripts/
│   │       ├── ingest_data.py
│   │       ├── transform_data.py
│   │       ├── load_to_postgres.py
│   ├── logs/
│   └── plugins/
├── postgres/
│   ├── 01-create-db.sql
│   └── 02-create-tables.sql
├── raw_data/
├── processed_data/
├── transformed_data/
├── requirements.txt
└── docker-compose.yaml
```
## Key Features
* Automated ETL orchestration using Apache Airflow
* Fully containerized execution with Docker Compose
* Task dependency management with retries and detailed logging
* Dual database integration (PostgreSQL and MongoDB)
* Automatic PostgreSQL schema initialization via startup SQL scripts
* Realistic production-style pipeline evolution
---
## Airflow DAGs
```
etl_pipeline
```
Tasks executed in order:
1. ingest_data: Cleans and normalizes raw CSV files.
3. transform_data: Performs feature engineering (e.g., age groups, derived columns).
4. load_to_postgres: Loads transformed data into a PostgreSQL relational database.
5. load_to_mongodb: Loads the same transformed dataset into MongoDB for NoSQL storage.

This design demonstrates parallel persistence into SQL and NoSQL databases from a single transformation step.

---

## How to Run Locally
__Prerequisites__
* Docker
* Docker Compose
* Git
  
__Setup__
```
git clone https://github.com/stvetang/Dataset-Preprocessing-Pipeline
cd dataset_pipeline
docker compose up -d
```

__Airflow UI__
```
http://localhost:8080
```

(Default credentials are defined in *docker-compose.yaml*.)

---

## Future Improvements
* Cloud deployment (AWS, GCP, or Azure)
* CI/CD integration
* API-based ingestion
* Data validation and unit testing
* Monitoring and alerting
* Analytics or machine learning layer

---
