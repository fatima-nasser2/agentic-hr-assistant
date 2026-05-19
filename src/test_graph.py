from src.graph.graph import build_graph

def test_full(question: str):
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
    # Test 1 — Clean HR question
    test_full("How many sick days do employees get?")

    # Test 2 — Multi-part HR question
    test_full("What is the parental leave policy and who is eligible?")

    # Test 3 — Triggers retry loop
    test_full("What happens with my benefits during leave?")

    # Test 4 — Out of scope
    test_full("What is the capital of France?")