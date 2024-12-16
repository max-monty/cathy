from r2r import R2RClient

def main():
    client = R2RClient("http://localhost:7272")
    
    print("Ask Cathy! (type 'quit' or 'exit' to end)")
    print("-" * 50)
    
    while True:
        query = input("\nEnter your query: ").strip()
        
        if query.lower() in ['quit', 'exit']:
            print("\nGoodbye!")
            break
            
        if not query:
            continue
            
        try:
            rag_response = client.retrieval.rag(
                query=query,
                rag_generation_config={"model": "openai/gpt-4o-mini", "temperature": 0.0},
            )
            results = rag_response["results"]
            
            print("\nAnswer:")
            print("-" * 50)
            print(results['completion']['choices'][0]['message']['content'])
            print("-" * 50)
            
        except Exception as e:
            print(f"\nError occurred: {str(e)}")

if __name__ == "__main__":
    main()