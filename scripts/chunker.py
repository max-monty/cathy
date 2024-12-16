import pandas as pd
from r2r import R2RClient
import json
import ast  # for safely evaluating string representation of list

client = R2RClient("http://localhost:7272")
df = pd.read_csv('./data/processed/nobles_sample_100.csv')

def transform_row(row):
    # Convert string representation of list to actual list
    classes = ast.literal_eval(row['Classes'])
    
    # Define subjects to exclude
    excluded_subjects = {'LUNCH', 'STUDY HALL', 'ADVISORY', 'ASSEMBLY', 'US: COLLEGE COUNSELING'}
    
    # Transform classes and filter out excluded subjects
    transformed_classes = [
        {
            "Course": c['Course'],
            "Subject": c['COURSE: Subject'],
            "Year": c['School Year']
        }
        for c in classes
        if c['COURSE: Subject'].upper() not in excluded_subjects
    ]
    
    # Create new transformed dictionary
    return {
        "Classes": transformed_classes,
        "Gender": row['Gender'],
        "Grade": int(row['Current Grade'].split()[1]),  # Extract number from "Grade 11"
        "City": row['City'],
        "Role": "Student",  # Simplify role
        "first_name": row['first_name'],
        "last_name": row['last_name']
    }

# Transform each row and create chunks
chunks = [json.dumps(transform_row(row)) for _, row in df.iterrows()]

ingest_response = client.documents.create(
    chunks=chunks,
    ingestion_mode="fast"
)

print(ingest_response)