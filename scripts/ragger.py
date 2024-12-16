from r2r import R2RClient

def main():
    # Initialize the client
    client = R2RClient("http://localhost:7272")
    
    print("RAG Query System (type 'quit' or 'exit' to end)")
    print("-" * 50)
    
    while True:
        # Get query from user
        query = input("\nEnter your query: ").strip()
        
        # Check for exit conditions
        if query.lower() in ['quit', 'exit']:
            print("\nGoodbye!")
            break
            
        # Skip empty queries
        if not query:
            continue
            
        try:
            # Process the query
            rag_response = client.retrieval.rag(
                query=query,
                rag_generation_config={"model": "openai/gpt-4o-mini", "temperature": 0.0},
            )
            results = rag_response["results"]
            
            # Print the response
            print("\nAnswer:")
            print("-" * 50)
            print(results['completion']['choices'][0]['message']['content'])
            print("-" * 50)
            
        except Exception as e:
            print(f"\nError occurred: {str(e)}")

if __name__ == "__main__":
    main()