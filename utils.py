def delete_all_documents(client):
    for doc in client.documents.list()["results"]:
        id = doc["id"]
        title = doc["title"]
        # bug: delete by id is not working
        # delete_response = client.documents.delete(id=id)
        delete_response = client.documents.delete_by_filter(
            {
                "document_id":
                {"$eq": id}
            }
        )
        print(id, title, delete_response)

def list_all_documents(client):
    for doc in client.documents.list()["results"]:
        id = doc["id"]
        title = doc["title"]
        print(id, title)

if __name__ == "__main__":
    import sys
    from r2r import R2RClient

    if len(sys.argv) < 2:
        print("Please provide a command: list or delete")
        sys.exit(1)

    command = sys.argv[1].lower()
    client = R2RClient("http://localhost:7272")

    if command == "list":
        list_all_documents(client)
    elif command == "delete":
        delete_all_documents(client)
    else:
        print("Invalid command. Use 'list' or 'delete'")
        sys.exit(1)


