import sqlite3
import os
import random
from faker import Faker
from datetime import datetime, timedelta, date

fake = Faker()

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "hr_database.db")

DEPARTMENTS = ["Engineering", "Product", "Marketing", "Sales", "People Operations", "Finance", "Legal"]
JOB_TITLES = {
    "Engineering": ["Junior Engineer", "Software Engineer", "Senior Engineer", "Lead Engineer", "Engineering Manager"],
    "Product": ["Product Analyst", "Product Manager", "Senior Product Manager", "Director of Product"],
    "Marketing": ["Marketing Coordinator", "Marketing Manager", "Senior Marketing Manager", "Head of Marketing"],
    "Sales": ["Sales Representative", "Account Executive", "Senior Account Executive", "Sales Manager"],
    "People Operations": ["HR Coordinator", "HR Manager", "Senior HR Manager", "Head of People"],
    "Finance": ["Financial Analyst", "Finance Manager", "Senior Finance Manager", "CFO"],
    "Legal": ["Legal Counsel", "Senior Legal Counsel", "Head of Legal"]
}

def create_database():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ── CREATE TABLES ─────────────────────────────────────
    cursor.executescript("""
    DROP TABLE IF EXISTS employees;
    DROP TABLE IF EXISTS leave_balances;
    DROP TABLE IF EXISTS payroll;

    CREATE TABLE employees (
        employee_id     TEXT PRIMARY KEY,
        name            TEXT NOT NULL,
        email           TEXT UNIQUE NOT NULL,
        department      TEXT NOT NULL,
        job_title       TEXT NOT NULL,
        hire_date       TEXT NOT NULL,
        manager_id      TEXT,
        status          TEXT DEFAULT 'active'
    );

    CREATE TABLE leave_balances (
        employee_id             TEXT PRIMARY KEY,
        annual_leave_remaining  INTEGER NOT NULL,
        sick_leave_remaining    INTEGER NOT NULL,
        parental_leave_eligible INTEGER NOT NULL,
        last_updated            TEXT NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    );

    CREATE TABLE payroll (
        employee_id         TEXT PRIMARY KEY,
        base_salary         INTEGER NOT NULL,
        last_bonus          INTEGER NOT NULL,
        last_review_date    TEXT NOT NULL,
        next_review_date    TEXT NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    );
    """)

    # ── GENERATE EMPLOYEES ────────────────────────────────
    employees = []
    managers = {}

    for i in range(1, 51):
        emp_id = f"EMP{i:03d}"
        department = random.choice(DEPARTMENTS)
        titles = JOB_TITLES[department]
        job_title = random.choice(titles)
        hire_date = fake.date_between(start_date="-5y", end_date="today")
        name = fake.name()
        email = f"{name.lower().replace(' ', '.').replace(',', '')}.{emp_id.lower()}@novatech.com"

        employees.append((
            emp_id, name, email, department,
            job_title, hire_date.strftime("%Y-%m-%d"),
            None, "active"
        ))

        if "Manager" in job_title or "Head" in job_title or "Director" in job_title or "Lead" in job_title:
            managers[department] = emp_id

    # ── ADD A KNOWN TEST EMPLOYEE ─────────────────────────
    employees.append((
        "EMP000", "Fatima Nasser", "fatima.nasser.emp000@novatech.com",
        "Engineering", "AI Engineer",
        "2023-01-15", managers.get("Engineering"),
        "active"
    ))

    # Assign managers
    employees_with_managers = []
    for emp in employees:
        emp_id, name, email, dept, title, hire_date, _, status = emp
        manager = managers.get(dept) if emp_id != managers.get(dept) else None
        employees_with_managers.append((emp_id, name, email, dept, title, hire_date, manager, status))

    cursor.executemany("""
        INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, employees_with_managers)

    # ── GENERATE LEAVE BALANCES ───────────────────────────
    leave_data = []
    for emp in employees_with_managers:
        emp_id = emp[0]
        leave_data.append((
            emp_id,
            random.randint(0, 21),   # annual leave remaining
            random.randint(0, 10),   # sick leave remaining
            random.choice([0, 1]),   # parental leave eligible
            datetime.now().strftime("%Y-%m-%d")
        ))

    cursor.executemany("""
        INSERT INTO leave_balances VALUES (?, ?, ?, ?, ?)
    """, leave_data)

    # ── GENERATE PAYROLL ──────────────────────────────────
    salary_ranges = {
        "Junior Engineer": (40000, 60000),
        "Software Engineer": (60000, 90000),
        "Senior Engineer": (90000, 130000),
        "Lead Engineer": (120000, 160000),
        "Engineering Manager": (140000, 180000),
        "AI Engineer": (70000, 110000),
        "Product Analyst": (45000, 65000),
        "Product Manager": (80000, 110000),
        "Senior Product Manager": (110000, 140000),
        "Director of Product": (140000, 170000),
        "Marketing Coordinator": (35000, 50000),
        "Marketing Manager": (60000, 85000),
        "Senior Marketing Manager": (85000, 110000),
        "Head of Marketing": (120000, 150000),
        "Sales Representative": (40000, 60000),
        "Account Executive": (55000, 80000),
        "Senior Account Executive": (75000, 100000),
        "Sales Manager": (90000, 120000),
        "HR Coordinator": (35000, 50000),
        "HR Manager": (55000, 75000),
        "Senior HR Manager": (75000, 100000),
        "Head of People": (110000, 140000),
        "Financial Analyst": (50000, 75000),
        "Finance Manager": (75000, 100000),
        "Senior Finance Manager": (100000, 130000),
        "CFO": (150000, 200000),
        "Legal Counsel": (80000, 110000),
        "Senior Legal Counsel": (110000, 140000),
        "Head of Legal": (140000, 170000),
    }

    payroll_data = []
    for emp in employees_with_managers:
        emp_id, _, _, _, job_title, hire_date, _, _ = emp
        min_sal, max_sal = salary_ranges.get(job_title, (50000, 80000))
        salary = random.randint(min_sal, max_sal)
        bonus = round(salary * random.uniform(0.05, 0.15))
        last_review = fake.date_between(start_date="-1y", end_date="today")
        next_review = last_review + timedelta(days=365)

        payroll_data.append((
            emp_id, salary, bonus,
            last_review.strftime("%Y-%m-%d"),
            next_review.strftime("%Y-%m-%d")
        ))

    cursor.executemany("""
        INSERT INTO payroll VALUES (?, ?, ?, ?, ?)
    """, payroll_data)

    conn.commit()
    conn.close()
    print(f"✅ Database created at {DB_PATH}")
    print(f"✅ 51 employees generated")
    print(f"✅ Leave balances generated")
    print(f"✅ Payroll records generated")

if __name__ == "__main__":
    create_database()