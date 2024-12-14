import pandas as pd
from r2r import R2RClient
import json

client = R2RClient("http://localhost:7272")

df = pd.read_csv('./data/nobles_sample_.csv')

# Convert each row to a JSON string
chunks = [json.dumps(row) for row in df.to_dict('records')]

# print(chunks[0])

ingest_response = client.documents.create(
    chunks=chunks,
    ingestion_mode="fast"
)

print(ingest_response)



