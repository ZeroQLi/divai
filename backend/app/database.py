import sqlite3
import os
import csv
from contextlib import contextmanager
from .config import settings

DB_PATH = settings.database_url.replace("sqlite:///", "")
CSV_PATH = settings.csv_path

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS applicants (
            applicant_id TEXT PRIMARY KEY,
            EMAIL_ID TEXT,
            APPLICATION_ID TEXT,
            LOAN_AMOUNT REAL,
            CURRENT_SALARY REAL,
            OVER_DUE_AMT REAL,
            OVER_DUE_MONTHS INTEGER,
            CURRENT_EMI_AMT REAL,
            NEW_EMI_AMT REAL,
            CREATED_DATE TEXT,
            STATUS TEXT,
            APPROVED_DATE TEXT,
            JUSTIFICATIONS TEXT,
            REMARKS TEXT,
            ADDITIONAL_MONTHS REAL,
            REMARKS_EN TEXT
        );
        """)
        db.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant_id TEXT,
            months_delayed INTEGER,
            overdue_amount REAL,
            current_salary REAL,
            remarks TEXT,
            agreement BOOLEAN,
            status TEXT,
            confidence REAL,
            explanation TEXT,
            audit_data TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)
        db.commit()


MAP = {
    "APPLICATION_ID": "APPLICATION_ID",
    "LOAN_AMOUNT": "LOAN_AMOUNT",
    "CURRENT_SALARY": "CURRENT_SALARY",
    "OVER_DUE_AMT": "OVER_DUE_AMT",
    "OVER_DUE_MONTHS": "OVER_DUE_MONTHS",
    "CURRENT_EMI_AMT": "CURRENT_EMI_AMT",
    "NEW_EMI_AMT": "NEW_EMI_AMT",
    "CREATED_DATE": "CREATED_DATE",
    "STATUS": "STATUS",
    "APPROVED_DATE": "APPROVED_DATE",
    "JUSTIFICATIONS": "JUSTIFICATIONS",
    "REMARKS": "REMARKS",
    "ADDITIONAL_MONTHS": "ADDITIONAL_MONTHS",
    "REMARKS_EN": "REMARKS_EN",
}
DB_COLS = ["applicant_id"] + list(MAP.keys())
PH = ",".join(["?"] * len(DB_COLS))

def seed_from_csv():
    with get_db() as db:
        row = db.execute("SELECT COUNT(*) FROM applicants").fetchone()
        if row[0] > 0:
            return
        if not os.path.exists(CSV_PATH):
            raise FileNotFoundError(f"CSV file '{CSV_PATH}' not found.")
        with open(CSV_PATH, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                return
            for csv_row in reader:
                applicant_id = csv_row.get("EDB_CUSTOMER_ID", "").strip()
                if not applicant_id:
                    continue
                vals = [applicant_id]
                for db_col, csv_col in MAP.items():
                    vals.append(csv_row.get(csv_col, None))
                db.execute(
                    f"INSERT OR REPLACE INTO applicants ({','.join(DB_COLS)}) VALUES ({PH})",
                    vals
                )
            db.commit()
