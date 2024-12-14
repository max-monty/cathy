from r2r import R2RClient

client = R2RClient("http://localhost:7272")

def extract_graph(client):
    document_id = client.documents.list()["results"][1]["id"]
    extract_response = client.documents.extract(document_id)
    # View extracted knowledge
    entities = client.documents.list_entities(document_id)
    relationships = client.documents.list_relationships(document_id)
    return document_id

def extract_graphs(client):
    documents = client.documents.list()["results"]
    for doc in documents:
        client.documents.extract(doc["id"])
        print(doc["id"] + " extracted")

def create_collection(client, document_id):
    # Create collection
    collection = client.collections.create(
        "Research Papers",
        "ML research papers with knowledge graph analysis"
    )
    collection_id = collection["results"]["id"]

    # Add documents to collection
    client.collections.add_document(collection_id, document_id)

    # # Optional, schedule extraction for all documents in the collection
    # client.graphs.extract(collection_id)

    # Pull document knowledge into collection graph
    pull_response = client.graphs.pull(collection_id)
    return collection_id, pull_response

def get_graph(client, collection_id):
    entities = client.graphs.list_entities(collection_id)
    relationships = client.graphs.list_relationships(collection_id)
    return entities, relationships

def graph_sync(client, collection_id, document_id):
    # client.documents.update(document_id, "new content") #TODO: look into this, i dont think this works/exists anymore
    client.documents.extract(document_id)
    response = client.graphs.pull(collection_id)
    return response

if __name__ == "__main__":
    # document_id = extract_graph(client)
    # collection_id, pull_response = create_collection(client, document_id)
    # print(pull_response)
    # entities, relationships = get_graph(client, collection_id)
    # response = graph_sync(client, collection_id, document_id)
    # print(relationships["results"][0])
    # print(entities["results"][0])

    # print(response)
    extract_graphs(client)

