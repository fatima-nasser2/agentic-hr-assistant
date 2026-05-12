from src.graph.graph import build_graph

def test_routing(question: str):
    graph = build_graph()

    initial_state = {
        "question": question,
        "rewritten_question": "",
        "documents": [],
        "generation": "",
        "retrieval_attempts": 0,
        "relevance": "",
        "route": ""
    }

    print(f"\n{'='*50}")
    print(f"❓ Question: {question}")
    print(f"{'='*50}")

    result = graph.invoke(initial_state)
    print(f"\n✅ Final answer: {result['generation']}")

if __name__ == "__main__":
    # Test 1 — should route to RAG
    test_routing("How many sick days do employees get?")

    # Test 2 — should route to RAG
    test_routing("What is the remote work policy?")

    # Test 3 — should route to unknown
    test_routing("What is the capital of France?")

    # Test 4 — should route to unknown
    test_routing("Can you write me a Python script?")