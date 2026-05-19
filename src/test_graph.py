from src.graph.graph import build_graph

def test_rag(question: str):
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

    print(f"\n{'='*55}")
    print(f"  QUESTION : {question}")
    print(f"{'='*55}")
    print("  -- Node trace --")

    result = graph.invoke(initial_state)

    print(f"\n  -- Result --")
    print(f"  Route      : {result.get('route', '—')}")
    print(f"  Rewritten  : {result.get('rewritten_question') or '(skipped)'}")
    print(f"  Docs found : {len(result.get('documents', []))}")
    print(f"  Attempts   : {result.get('retrieval_attempts', 0)}")
    print(f"  Relevance  : {result.get('relevance') or '—'}")
    print(f"  Answer     : {result['generation']}")
    print(f"{'='*55}")

if __name__ == "__main__":
    # Test 1 — HR question
    test_rag("How many sick days do employees get?")

    # Test 2 — HR question
    test_rag("What is the parental leave policy?")

    # Test 3 — Out of scope
    test_rag("What is the capital of France?")