import sqlite3
import os
import uuid
from datetime import datetime
from typing import List
from langchain_core.documents import Document

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "hr_database.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_employee_info(employee_id: str) -> dict | None:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.*, lb.annual_leave_remaining, lb.sick_leave_remaining,
                   lb.parental_leave_eligible, p.base_salary, p.last_bonus,
                   p.last_review_date, p.next_review_date
            FROM employees e
            LEFT JOIN leave_balances lb ON e.employee_id = lb.employee_id
            LEFT JOIN payroll p ON e.employee_id = p.employee_id
            WHERE e.employee_id = ?
        """, (employee_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def query_to_documents(employee_id: str, question: str) -> List[Document]:
    """Convert SQL query results into Document objects for the RAG pipeline"""
    data = get_employee_info(employee_id)

    if not data:
        return [Document(
            page_content=f"No employee found with ID: {employee_id}",
            metadata={"source": "sql_database"}
        )]

    # Format as readable text
    content = f"""
Employee Record for {data['name']} ({data['employee_id']}):

Personal Information:
- Name: {data['name']}
- Email: {data['email']}
- Department: {data['department']}
- Job Title: {data['job_title']}
- Hire Date: {data['hire_date']}
- Status: {data['status']}

Leave Balances:
- Annual Leave Remaining: {data['annual_leave_remaining']} days
- Sick Leave Remaining: {data['sick_leave_remaining']} days
- Parental Leave Eligible: {'Yes' if data['parental_leave_eligible'] else 'No'}

Payroll Information:
- Base Salary: ${data['base_salary']:,}
- Last Bonus: ${data['last_bonus']:,}
- Last Review Date: {data['last_review_date']}
- Next Review Date: {data['next_review_date']}
""".strip()

    return [Document(
        page_content=content,
        metadata={"source": "sql_database", "employee_id": employee_id}
    )]


# ── EVALUATIONS ───────────────────────────────────────────

def ensure_evaluations_table():
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                eval_id             TEXT PRIMARY KEY,
                employee_id         TEXT NOT NULL,
                thread_id           TEXT NOT NULL,
                question            TEXT NOT NULL,
                answer              TEXT NOT NULL,
                retrieval_source    TEXT NOT NULL,
                groundedness_score  REAL NOT NULL,
                relevance_score     REAL NOT NULL,
                completeness_score  REAL NOT NULL,
                overall_score       REAL NOT NULL,
                reasoning           TEXT NOT NULL,
                timestamp           TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def save_evaluation(
    employee_id: str,
    thread_id: str,
    question: str,
    answer: str,
    retrieval_source: str,
    groundedness: float,
    relevance: float,
    completeness: float,
    overall: float,
    reasoning: str,
) -> str:
    eval_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO evaluations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (eval_id, employee_id, thread_id, question, answer, retrieval_source,
             groundedness, relevance, completeness, overall, reasoning, timestamp),
        )
        conn.commit()
    finally:
        conn.close()
    return eval_id