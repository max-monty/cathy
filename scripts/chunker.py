import pandas as pd
from r2r import R2RClient
import json
import ast  

client = R2RClient("http://localhost:7272")
df = pd.read_csv('./data/processed/nobles_sample_100.csv')

def transform_row(row):
    classes = ast.literal_eval(row['Classes'])
    
    excluded_subjects = {'LUNCH', 'STUDY HALL', 'ADVISORY', 'ASSEMBLY', 'US: COLLEGE COUNSELING'}
    
    transformed_classes = [
        {
            "Course": c['Course'],
            "Subject": c['COURSE: Subject'],
            "Year": c['School Year']
        }
        for c in classes
        if c['COURSE: Subject'].upper() not in excluded_subjects
    ]
    
    return {
        "Classes": transformed_classes,
        "Gender": row['Gender'],
        "Grade": int(row['Current Grade'].split()[1]),  
        "City": row['City'],
        "Role": "Student",  
        "first_name": row['first_name'],
        "last_name": row['last_name']
    }

chunks = [json.dumps(transform_row(row)) for _, row in df.iterrows()]

ingest_response = client.documents.create(
    chunks=chunks,
    ingestion_mode="fast"
)

print(ingest_response)