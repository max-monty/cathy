from r2r import R2RClient

client = R2RClient("http://localhost:7272")

# Call RAG directly
rag_response = client.retrieval.rag(
    query="what do you know about michael levine?",
    rag_generation_config={"model": "openai/gpt-4o-mini", "temperature": 0.0},
)
results = rag_response["results"]

# print(f"Search Results:\n{results['search_results']}")

print(f"Answer:\n{results['completion']['choices'][0]['message']['content']}")