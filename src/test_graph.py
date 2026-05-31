import sys
import os
import uuid
from datetime import datetime
from src.graph.graph import build_graph


class Tee:
    """Mirror all print output to both stdout and a file."""
    def __init__(self, file):
        self.terminal = sys.__stdout__
        self.file = file

    def write(self, message):
        self.terminal.write(message)
        self.file.write(message)

    def flush(self):
        self.terminal.flush()
        self.file.flush()


def run_test(graph, question: str, employee_id: str = ""):
    initial_state = {
        "question": question,
        "rewritten_question": "",
        "documents": [],
        "generation": "",
        "retrieval_attempts": 0,
        "relevance": "",
        "route": "",
        "retrieval_source": "",
        "chat_history": [],
        "employee_id": employee_id
    }

    print(f"\n{'='*55}")
    print(f"  QUESTION    : {question}")
    print(f"  EMPLOYEE ID : {employee_id or '(not provided)'}")
    print(f"{'='*55}")
    print("  -- Node trace --")

    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    result = graph.invoke(initial_state, config=config)

    print(f"\n  -- Result --")
    print(f"  Route      : {result.get('route', '—')}")
    print(f"  Source     : {result.get('retrieval_source', '—')}")
    print(f"  Rewritten  : {result.get('rewritten_question') or '(skipped)'}")
    print(f"  Docs found : {len(result.get('documents', []))}")
    print(f"  Attempts   : {result.get('retrieval_attempts', 0)}")
    print(f"  Relevance  : {result.get('relevance') or '—'}")
    print(f"  Answer     : {result['generation']}")
    print(f"{'='*55}")


# ── TEST CASES ────────────────────────────────────────────

TESTS = {
    # "FAISS - SOURCE ROUTING": [
    #     "What is the sick leave policy?",
    #     "How does the hiring process work?",
    # ],
    # "SQL - SOURCE ROUTING": [
    #     ("How many sick days do I have left?", "EMP000"),
    #     ("When is my next performance review?", "EMP000"),
    #     ("How many sick days do I have left?", ""),   # no ID — should ask for it
    # ],
    "Internal KB - SOURCE ROUTING": [
        "Who is the CTO of Fatinova Technologies?",
        "Who is on the engineering team?",
        "What tools does Fatinova Technologies use for project management?",
        "What happens in my first 30 days?",
        "How do I request new software?",
        "What should I do on my first day?",
        "How do I set up my laptop?",
    ],
    # "Web - SOURCE ROUTING": [
    #     "What are the latest labor laws in Lebanon?",
    #     "What is the average salary for an AI Engineer in 2026?",
    # ],
}

# ── RUNNER ────────────────────────────────────────────────

if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"outputs/test_results_{timestamp}.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        sys.stdout = Tee(f)
        try:
            print("HR ASSISTANT — TEST RUN")
            print(f"Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Total tests: {sum(len(v) for v in TESTS.values())}")

            graph = build_graph()

            for category, questions in TESTS.items():
                print(f"\n\n{'#'*55}")
                print(f"  CATEGORY: {category}  ({len(questions)} tests)")
                print(f"{'#'*55}")
                for item in questions:
                    if isinstance(item, tuple):
                        question, employee_id = item
                    else:
                        question, employee_id = item, ""
                    run_test(graph, question, employee_id)

        finally:
            sys.stdout = sys.__stdout__

    print(f"\nDone. Results saved to: {output_file}")
