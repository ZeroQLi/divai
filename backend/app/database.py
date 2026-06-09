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
            ID TEXT, APPLICANT TEXT, APPLICATION_ID TEXT, AGREEMENT_ID TEXT, EDB_LOAN_ID TEXT, EDB_CUSTOMER_ID TEXT, REQUEST_TYPE TEXT, LOAN_AMOUNT REAL, CURRENT_SALARY REAL, OVER_DUE_AMT REAL, OVER_DUE_MONTHS INTEGER,
            DEDUCT_FROM_SALARY TEXT, APPROVED_REQUEST_TYPE TEXT, NEW_EMI_APPLICABLE_MONTHS TEXT, CURRENT_EMI_AMT REAL, NEW_EMI_AMT REAL, CREATED_DATE TEXT, CREATED_BY TEXT, STATUS TEXT, APPROVED_DATE TEXT, JUSTIFICATIONS TEXT, REMARKS TEXT, UNTIL_LOAN_END REAL, ADDITIONAL_MONTHS REAL, ADDITIONAL_PREMIUM REAL, AUTH_SIGNATORY TEXT, START_MONTH TEXT, START_YEAR TEXT, YEAR TEXT, REMARKS_EN TEXT
        );
        """)
        db.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant_id TEXT,
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
            cols = ",".join(reader.fieldnames)
            placeholders = ",".join(["?"] * len(reader.fieldnames))
            for csv_row in reader:
                applicant_id = csv_row.get("EDB_CUSTOMER_ID", "").strip()
                if not applicant_id:
                    applicant_id = csv_row.get("APPLICANT", "").strip()
                if not applicant_id:
                    continue
                row_values = [csv_row.get(col, None) for col in reader.fieldnames]
                values = [applicant_id] + row_values
                db.execute(
                    f"INSERT OR REPLACE INTO applicants (applicant_id,{cols}) VALUES (?,{placeholders})",
                    values
                )
            db.commit()
