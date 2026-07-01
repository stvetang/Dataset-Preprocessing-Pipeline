# ETL Data Pipeline with Airflow, PostgreSQL, MongoDB, and REST API

## Overview

This project is an end-to-end ETL (Extract, Transform, Load) data pipeline built with Python and orchestrated using Apache Airflow, fully containerized with Docker. It ingests raw CSV datasets, performs data cleaning, transformation, and ML-powered anomaly detection, enriches records using an LLM API, and stores processed results in both PostgreSQL (SQL) and MongoDB (NoSQL) databases. The pipeline is accessible via a RESTful API built with FastAPI, enabling programmatic data access and automated file ingestion.

The project demonstrates a production-ready data engineering architecture with automation, orchestration, containerization, polyglot persistence, machine learning integration, LLM-powered enrichment, and API-driven interactions.

---

## Architecture

### System Architecture Diagram

```text
┌────────────────────────────────────────────────────────────────────┐
│                        Docker Network (airflow)                    │
│                                                                    │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐                  │
│  │ FastAPI  │      │  Airflow │      │  Airflow │                  │
│  │   API    │◄─────┤Webserver │◄─────┤Scheduler │                  │
│  └────┬─────┘      └──────────┘      └──────┬───┘                  │
│       │                                     │                      │
│       │            ┌────────────────────────┼──────────────┐       │
│       │            │   ETL Pipeline         │              │       │
│       │            │                        ▼              │       │
│       │            │  ┌────────┐    ┌──────────────┐       │       │
│       │            │  │ Ingest │───►│  Transform   │       │       │
│       │            │  └────────┘    └──────┬───────┘       │       │
│       │            │                       │               │       │
│       │            │                       ▼               │       │
│       │            │           ┌───────────────────┐       │       │
│       │            │           │ Detect Anomalies  │       │       │
│       │            │           │  (IsolationForest)│       │       │
│       │            │           └──────────┬────────┘       │       │
│       │            │                      │                │       │
│       │            │                      ▼                │       │
│       │            │           ┌───────────────────┐       │       │
│       │            │           │  Enrich with LLM  │       │       │
│       │            │           │   (OpenAI API)    │       │       │
│       │            │           └────┬──────────┬───┘       │       │
│       │            │                │          │           │       │
│       │            │                ▼          ▼           │       │
│       │            │  ┌─────────────────┐ ┌─────────┐      │       │
│       ├────────────┼─►│   PostgreSQL    │ │ MongoDB │      │       │
│       └────────────┼─►│  (Relational)  │ │(Document│       │       │
│                    │  └─────────────────┘ └─────────┘      │       │
│                    └───────────────────────────────────────┘       │
└────────────────────────────────────────────────────────────────────┘
         ▲                                               ▲
         │                                               │
    HTTP Requests                                 Airflow Web UI
    (Port 5000)                                    (Port 8080)
```

### ETL Pipeline Flow

```text
Raw CSV Data
   │
   ├─► API Upload (POST /api/upload)
   │        OR
   └─► Manual file placement
   │
   ▼
Ingest (clean & normalize)
   │
   ▼
Transform (feature engineering)
   │
   ▼
Detect Anomalies (ML - IsolationForest)
   │
   ▼
Enrich with LLM (OpenAI API - categorization & quality notes)
   │
   ├──────────────────┐
   ▼                  ▼
PostgreSQL         MongoDB
(Relational)       (Document)
   │                  │
   └──────────────────┘
            │
            ▼
      API Access
   (GET /api/data)
```

---

## Technologies Used

**Backend & Orchestration:**
- Python 3.9
- Apache Airflow 2.10.2
- FastAPI
- Uvicorn

**Databases:**
- PostgreSQL 13
- MongoDB 6

**Data Processing:**
- pandas
- numpy
- scikit-learn
- psycopg2
- pymongo

**AI/LLM Integration:
- OpenAI API (gpt-4o-mini) 

**Infrastructure:**
- Docker
- Docker Compose
- Linux-based container environments

---

## Project Structure

```
dataset_pipeline/
├── api/
│   ├── Dockerfile
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # API dependencies
├── airflow/
│   ├── dags/
│   │   ├── etl_pipeline_dag.py
│   │   ├── .airflowignore       # Prevents scanner from parsing scripts/
│   │   ├── raw_data/            # Input CSV files
│   │   ├── processed_data/      # Cleaned data
│   │   ├── transformed_data/    # Feature-engineered data
│   │   ├── anomaly_data/        # Data with anomaly detection results
│   │   ├── enriched_data/       # Final enriched data (LLM output)
│   │   └── scripts/
│   │       ├── ingest_data.py
│   │       ├── transform_data.py
│   │       ├── detect_anomalies.py   # ML anomaly detection stage
│   │       ├── enrich_with_llm.py    # LLM enrichment stage
│   │       ├── load_to_postgres.py
│   │       └── load_to_mongodb.py
│   ├── logs/
│   └── plugins/
├── postgres/
│   ├── 01-create-db.sql
│   └── 02-create-tables.sql
├── .env                     # API key storage (never committed to git)
├── .gitignore
├── docker-compose.yaml      # Orchestrates all services
└── requirements.txt         # Airflow dependencies
```

---

## Key Features

- **Automated ETL Orchestration** - Apache Airflow manages task scheduling and dependencies
- **ML-Powered Anomaly Detection** — scikit-learn IsolationForest flags outlier records inline in the pipeline before loading
- **LLM Data Enrichment** — OpenAI API classifies each record and generates plain-English data quality notes automatically  
- **RESTful API** - FastAPI provides programmatic access to pipeline data and operations  
- **Containerized Architecture** - Fully Dockerized microservices with Docker Compose  
- **Polyglot Persistence** - Dual database integration (PostgreSQL for relational, MongoDB for document storage)  
- **File Upload API** - Automated CSV ingestion via HTTP POST requests    
- **Retry Logic** - Airflow handles failures with automatic retries
- **Health Monitoring** - API endpoints for service health checks  
- **Interactive Documentation** - Auto-generated Swagger UI at `/docs`  

---

## Airflow DAG

**DAG Name:** `etl_pipeline`  
**Schedule:** Daily (`@daily`)

**Task Execution Order:**
1. **ingest_data** - Cleans and normalizes raw CSV files (handles missing values, standardizes formats)
2. **transform_data** - Performs feature engineering (age groups, name length, email domain extraction)
3. **load_to_postgres** - Loads transformed data into PostgreSQL relational database
4. **load_to_mongodb** - Loads transformed data into MongoDB document database

**Task Dependencies:**
```
ingest >> transform >> detect_anomalies >> enrich_with_llm >> [load_postgres, load_mongodb]
```

The final two load tasks run in parallel, demonstrating concurrent writes to SQL and NoSQL databases from a single enriched dataset.

---

## ML & AI Pipeline Stages

**Anomaly Detection (detect_anomalies.py)**

Uses scikit-learn's IsolationForest — an unsupervised machine learning algorithm — to flag records that deviate significantly from the rest of the dataset. No labeled training data is required; the model learns what "normal" looks like from the data itself.

Features used: age, name_length, email_domain (label-encoded).

New columns added:
- is_anomaly (Boolean) — True if the record is flagged as an outlier
- anomaly_score (Float) — Raw isolation score; more negative means more anomalous

**LLM Enrichment (enrich_with_llm.py)**

Calls the OpenAI API (gpt-4o-mini) for each record with a dynamically generated prompt. The model returns structured JSON containing a user category classification and a data quality assessment. Includes retry logic with exponential backoff to handle transient API failures gracefully.

New columns added:
- predicted_category — one of: personal, business, academic, government, unknown
- data_quality_notes — plain-English assessment of the record's quality

---

## API Layer

The project includes a **FastAPI-based REST API** that provides programmatic access to the ETL pipeline:

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check for API and database connections |
| GET | `/api/data` | Retrieve transformed data with pagination support |
| GET | `/api/data/{id}` | Get specific record by ID |
| POST | `/api/upload` | Upload CSV files for processing |
| GET | `/api/mongodb/data` | Query data from MongoDB |
| GET | `/api/stats` | Summary statistics and distributions |
| DELETE | `/api/data/{id}` | Delete records from database |

### Interactive API Documentation

Visit **`http://localhost:5000/docs`** for automatically generated Swagger UI documentation where you can test all endpoints interactively.

### Example Usage

**Get all data:**
```bash
curl http://localhost:5000/api/data
```

**Upload new CSV:**
```bash
curl -X POST http://localhost:5000/api/upload -F "file=@employees.csv"
```

**Get statistics:**
```bash
curl http://localhost:5000/api/stats
```

**Check system health:**
```bash
curl http://localhost:5000/api/health
```

**Example Response (GET /api/data):**
```json
{
  "count": 6,
  "limit": 100,
  "offset": 0,
  "data": [
    {
      "id": 1,
      "name": "Alice",
      "age": 25,
      "email": "alice@example.com",
      "age_group": "Adult",
      "name_length": 5,
      "email_domain": "example.com"
    }
  ]
}
```

---

## How to Run Locally

### Prerequisites
- Docker Desktop (or Docker Engine + Docker Compose)
- Git

### Setup

**1. Clone the repository:**
```bash
git clone https://github.com/stvetang/Dataset-Preprocessing-Pipeline
cd dataset_pipeline
```

**2. Start all services:**
```bash
docker compose up -d
```

**3. Wait for services to initialize** (approximately 30-60 seconds)

**4. Access the applications:**

- **Airflow UI:** http://localhost:8080
  - Username: `admin`
  - Password: `admin`
  
- **API Documentation:** http://localhost:5000/docs

- **API Endpoints:** http://localhost:5000/api/*

**5. Trigger the ETL pipeline:**
- Open Airflow UI at http://localhost:8080
- Navigate to the `etl_pipeline` DAG
- Click the "Play" button to trigger a manual run

### Stopping the Services

```bash
docker compose down
```

### Rebuilding After Code Changes

```bash
docker compose down
docker compose up -d --build
```

---

## Sample Data Flow

**Input (raw_data/sample1.csv):**
```csv
name,age,email
Alice,25,alice@example.com
Bob,30,bob@example.com
Charlie,,charlie@example.com
```

**After Ingest (processed_data/sample1.csv):**
- Missing age filled with mean (27.5)
- Names title-cased
- Emails lowercased

**After Transform (transformed_data/sample1.csv):**
```csv
name,age,email,age_group,name_length,email_domain
Alice,25.0,alice@example.com,Adult,5,example.com
Bob,30.0,bob@example.com,Adult,3,example.com
Charlie,27.5,charlie@example.com,Adult,7,example.com
```

**Loaded to PostgreSQL and MongoDB** - Queryable via API endpoints

---

## Technical Highlights

### Docker Networking
All services run on a shared Docker network (`airflow`), enabling inter-service communication using service names as hostnames (e.g., `postgres`, `mongodb`, `webserver`).

### Database Abstraction
The API provides a unified interface to query both SQL and NoSQL databases, demonstrating polyglot persistence without exposing database credentials to clients.

### Error Handling
- API returns appropriate HTTP status codes (200, 404, 500)
- Database transactions with rollback on failure
- File validation during upload (CSV format, pandas parsing)

### Pagination
API endpoints support `limit` and `offset` parameters for efficient large dataset handling.

---

## Future Improvements

- [ ] Cloud deployment (AWS ECS, RDS, DocumentDB)
- [ ] CI/CD pipeline with GitHub Actions
- [x] ~~API-based ingestion~~
- [x] ~~ML anomaly detection pipeline stage~~
- [x] ~~LLM enrichment pipeline stage~~
- [ ] JWT authentication for API
- [ ] Data validation with Great Expectations
- [ ] Monitoring and alerting (Prometheus, Grafana)
- [ ] Unit and integration tests
- [ ] API rate limiting
- [ ] Data versioning

---
