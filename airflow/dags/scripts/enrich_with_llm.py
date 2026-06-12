import os
import json
import time
import pandas as pd
from openai import OpenAI

anomaly_data_folder = "/opt/airflow/dags/anomaly_data"
enriched_data_folder = "/opt/airflow/dags/enriched_data"
os.makedirs(enriched_data_folder, exist_ok=True)

# Initializing the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def build_prompt(row: dict) -> str:
    
    return f"""You are a data quality assistant. Analyze the user record and respond with a JSON object, no explanation or markdown.

    Record:
    - Name: {row.get('name', 'unkown')}
    - Age: {row.get('age', 'unknown')}
    - Email domain: {row.get('email_domain', 'unknown')}
    - Flagged as anomaly: {row.get('is_anomaly', False)}

    Return exactly this JSON format:
    {{
        "predicted_category": "<one of: personal, businexx, academic, government, unknown>",
        "data_quality_notes": "<one sentence describing any data quality concerns or confirming the record looks clean>"
    }}"""

def call_llm(prompt: str, retries: int = 3) -> dict:

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                message=[
                    {"role": "system", "content": "You are a data quality assistant. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.2,
            )
            # Raw text response from the LLM
            raw_text = response.choices[0].message.content.strip()
            return json.loads(raw_text)
        
        except json.JSONDecodeError:
            print(f"Attempt {attempt + 1}: Could not parse LLM response as JSON. Retrying.")
            time.sleep(1)

        except Exception as e:
            print(f"Attempt {attempt + 1}: API call failed with error {e}. Retrying.")
            time.sleep(2 ** attempt)

        print("Retries failed. Returning fallback values for record.")
        return {
            "predicted_category": "unknown",
            "data_quality_notes": "LLM enrichement failed: could not reach API."
        }
    
# Process each anomaly data file
files = os.listdir(anomaly_data_folder)
print("Files in anomaly data folder:", files)

for file_name in files:
    if not file_name.endswith(".csv"):
        continue

    file_path = os.path.join(anomaly_data_folder, file_name)
    df = pd.read_csv(file_path)

    predicted_categories = []
    quality_notes = []      

    # Loop through each row and enrich with LLM
    for idx, row in df.iterrows():
        print(f" Enriching record {idx + 1}/{len(df)}")

        prompt = build_prompt(row.to_dict())
        result = call_llm(prompt)

        predicted_categories.append(result.get("predicted_category", "unknown"))
        quality_notes.append(result.get("data_quality_notes", ""))
        time.sleep(0.5)

    df['predicted_category'] = predicted_categories
    df['data_quality_notes'] = quality_notes

    # Saving enriched data to new folder
    output_path = os.path.join(enriched_data_folder, file_name)
    df.to_csv(output_path, index=False)

    print(f"\nEnriched {file_name} saved to {output_path}")
    print(df[['name', 'email_domain', 'predicted_category', 'data_quality_notes']].head())
            
             