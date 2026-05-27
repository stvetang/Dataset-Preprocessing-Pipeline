CREATE TABLE IF NOT EXISTS transformed_data ( 
    id SERIAL PRIMARY KEY,
    name TEXT,
    age INTEGER,
    email TEXT,
    age_group TEXT,
    name_length INTEGER,
    email_domain TEXT,

    is_anomaly BOOLEAN,             -- True if IsolationForest flags record as outlier
    anomaly_score NUMERIC(8, 4),    -- Float score: more negative means more anomalous
    
    predicted_category TEXT,
    data_quality_notes TEXT,
);

