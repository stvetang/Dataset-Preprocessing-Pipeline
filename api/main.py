from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import psycopg2
from pymongo import MongoClient
import os
from typing import Optional, List, Dict 
import pandas as pd

app = FastAPI(title="ETL Pipeline API", version="1.0.0")

POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "database": os.getenv("POSTGRES_DB", "etl_project"),
    "user": os.getenv("POSTGRES_USER", "airflow"),
    "password": os.getenv("POSTGRES_PASSWORD", "airflow"),
    "port": os.getenv("POSTGRES_PORT", "5432")                          
}

MONGO_HOST = os.getenv("MONGO_HOST", "mongodb")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))

RAW_DATA_PATH = "/app/raw_data/"

def get_postgres_connection():
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        return conn
    except Exception as e:
        raise HTTPException(statis_code=500, detail=f"Databse connection failed: str{(e)}")
    
def get_mongo_client():
    try:
        client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
        return client 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB connection failed: {str(e)}")
    

@app.get("/")
def root():
    """Root endpoint - API information"""
    return {
        "message": "ETL Pipeline API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "data": "/api/data",
            "upload": "/api/upload",
            "mongodb": "/api/mongodb/data",
            "stats": "/api/stats"
        }
    }


@app.get("/api/health")
def health_check():
    """Check if API and database connections are healthy"""
    health_status = {
        "api": "healthy",
        "postgres": "unknown",
        "mongodb": "unknown"
    }

    try: 
        conn = get_postgres_connection()
        conn.close()
        health_status["postgres"] = "healthy"
    except Exception as e:
        health_status["postgres"] = f"unhealthy: {str(e)}"

    try:
        client = get_mongo_client()
        client.server_info()
        health_status["mongodb"] = "healthy"
        client.close()
    except Exception as e:
        health_status["mongodb"] = f"unhealthy: {str(e)}"

    return health_status


@app.get("/api/data")
def get_all_data(limit: Optional[int] = 100, offset: Optional[int] = 0):
    """Get all transformed data from postgreSQL"""
    conn = get_postgres_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT id, name, age, email, age_grup, name_length, email_domain
            FROM transformed_data
            ORDER BY id
            LIMIT %s OFFSET %s
            """,
            (limit, offset)
        )

        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()

        data = [dict(zip(columns, rows)) for now in rows]

        return {
            "count": len(data),
            "limit": limit,
            "offset": offset,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
    finally:
        cur.close()
        conn.close()    


@app.get("/api/data/{record_id}")
def get_data_by_id(record_id: int):
    """Get specific record by ID from PostgreSQL"""
    conn = get_postgres_connection()
    cur = conn.cursor()
    
    try:
        cur.execute(
            """
            SELECT id, name, age, email, age_group, name_length, email_domain
            FROM transformed_data
            WHERE id = %s
            """
            (record_id,)
        )

        row = cur.fetchome()

        if row is None:
            raise HTTPException(status_code=404, detail=f"Record with id {record_id} not found")
        
        columns = [desc[0] for desc in cur.description]
        data = dict(zip(columns, row))

        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
    finally:
        cur.close()
        conn.close()


@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload a CSV file to the raw_data folder"""
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(sttaus_code=400, detail="Only CSV files are allowed")
    
    try:
        # Ensure raw_data directory exists
        os.makedirs(RAW_DATA_PATH, exist_ok=True)

        # Save the uploaded file 
        file_path = os.path.join(RAW_DATA_PATH, file.filename)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Validate CSV structure
        try:
            df = pd.read_csv(file_path)
            row_count = len(df)
            columns = list(df.columns)
        except Exception as e:
            os.remove(file_path) # Remove invalid file
            raise HTTPException(status_code=400, detail=f"Invalid CSV format: {str(e)}")
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename, 
            "path": file_path,
            "rows": row_count,
            "columns": columns
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@app.get("/api/mongodb/data")
def get_mongodb_data(limit: Optional[int] = 100):
    """Get data from MongoDB"""
    client = get_mongo_client()
    
    try:
        db = client["dataset_pipeline"]
        collection = db["employees"]

        # Fetch documents (excluding MongoDB's internal _id field)
        documents = list(collection.find({}, {"_id": 0}).limit(limit))

        return {
            "count": len(documents),
            "limit": limit,
            "data": documents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB query failed: {str(e)}")
    finally:
        client.close()


@app.get("/api/stats")
def get_statistics():
    """Get summary statistics from PostgreSQL"""
    conn = get_postgres_connection()
    cur = conn.cursor()

    try:
        # Total records
        cur.execute("SELECT COUNT(*) FROM transformed_data")
        total_records = cur.fetchone()[0]

        # Average age
        cur.execute("SELECT AVG(age) FROM transformed_data")
        avg_age = cur.fetchone()[0]

        # Age group distribution
        cur.execute(
            """
            SELECT age_group, COUNT(*) as count
            FROM transformed_data
            GROUP BY age_group
            """
        )
        age_groups = {row[0]: row[1] for row in cur.fetchall()}

        # Email domain distribution
        cur.execute(
            """
            SELECT email_domain, COUNT(*) as count
            FROM transformed_data
            GROUP BY email_domain
            ORDER BY count DESC
            LIMIT 5
            """
        )
        top_domains = {row[0]: row[1] for row in cur.fetchall()}

        return {
            "total_records": total_records,
            "average_age": round(float(avg_age), 3) if avg_age else 0,
            "age_group_distribution": age_groups,
            "top_email_domains": top_domains
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statstics query failed: {str(e)}")
    finally:
        cur.close()
        conn.close()


@app.delete("/api/data/{record_id}")
def delete_record(record_id: int):
    """Delete a specific record from PostgreSQL"""
    conn = get_postgres_connection()
    cur = conn.cursor()

    try:
        # Check if record exists
        cur.execute("SELECT id FROM transformed_data WHERE id = %s", (record_id,))
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail=f"Record with id {record_id} not found")
                                
        # Delete the record
        cur.execute("DELETE FROM transformed_data WHERE id = %s", (record_id,))
        conn.commit()

        return {
            "message": f"Record {record_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
    finally:
        cur.close()
        conn.close()    