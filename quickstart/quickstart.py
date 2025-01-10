import r2r

client = r2r.R2RClient()

# client.documents.create(
#     file_path="quickstart/aristotle.txt",
# )

# response = client.retrieval.search(
#   query="Who was aristotle?",
# )
# print(response["results"]["chunk_search_results"][0]["text"])

# response = client.retrieval.rag(
#   query="Who was aristotle?",
# )
# print(response["results"]["completion"]["choices"][0]["message"]["content"])

client.documents.create(
    file_path="quickstart/excel.txt"
)

response = client.retrieval.rag(
  query="tell me about excel trips"
)
print(response["results"]["completion"]["choices"][0]["message"]["content"])