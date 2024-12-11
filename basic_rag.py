from r2r import R2RClient

client = R2RClient("http://localhost:7272")

# comment out after first run of script to prevent error when attempting to reingest
# with open("test.txt", "w") as file:
#     file.write("John is a person that works at Google.")

# client.documents.create(file_path="test.txt")

# Call RAG directly
rag_response = client.retrieval.rag(
    query="Who is john",
    rag_generation_config={"model": "openai/gpt-4o-mini", "temperature": 0.0},
)
results = rag_response["results"]

print(f"Search Results:\n{results['search_results']}")
# {'chunk_search_results': [{'chunk_id': 'b9f40dbd-2c8e-5c0a-8454-027ac45cb0ed', 'document_id': '7c319fbe-ca61-5770-bae2-c3d0eaa8f45c', 'user_id': '2acb499e-8428-543b-bd85-0d9098718220', 'collection_ids': ['122fdf6a-e116-546b-a8f6-e4cb2e2c0a09'], 'score': 0.6847735847465275, 'text': 'John is a person that works at Google.', 'metadata': {'version': 'v0', 'chunk_order': 0, 'document_type': 'txt', 'associated_query': 'Who is john'}}], 'kg_search_results': []}

print(f"Completion:\n{results['completion']}")
# {'id': 'chatcmpl-AV1Sc9DORfHvq7yrmukxfJPDV5dCB', 'choices': [{'finish_reason': 'stop', 'index': 0, 'logprobs': None, 'message': {'content': 'John is a person that works at Google [1].', 'refusal': None, 'role': 'assistant', 'audio': None, 'function_call': None, 'tool_calls': None}}], 'created': 1731957146, 'model': 'gpt-4o-mini', 'object': 'chat.completion', 'service_tier': None, 'system_fingerprint': 'fp_04751d0b65', 'usage': {'completion_tokens': 11, 'prompt_tokens': 145, 'total_tokens': 156, 'completion_tokens_details': None, 'prompt_tokens_details': None}}
