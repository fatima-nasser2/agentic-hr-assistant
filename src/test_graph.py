from src.graph.graph import build_graph

def test_graph():
    graph = build_graph()

    # Test input
    initial_state = {
        "question": "How many sick days do employees get?",
        "rewritten_question": "",
        "documents": [],
        "generation": "",
        "retrieval_attempts": 0,
        "relevance": "",
        "route": ""
    }

    print("\n🚀 Running graph...\n")
    result = graph.invoke(initial_state)

    print("\n✅ Graph completed!")
    print(f"Final answer: {result['generation']}")

if __name__ == "__main__":
    test_graph()