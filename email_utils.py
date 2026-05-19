import sqlite3
from datetime import datetime

DB_NAME = "emails.db"

def init_db():
    """Initializes the SQLite database and creates the emails table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient_email TEXT NOT NULL,
            first_name TEXT,
            company_name TEXT,
            subject TEXT NOT NULL,
            body_html TEXT NOT NULL,
            message_id TEXT,
            status TEXT NOT NULL, -- 'SENT', 'FAILED'
            error_msg TEXT,
            sent_time TIMESTAMP,
            campaign_id TEXT,
            email_type TEXT DEFAULT 'initial' -- 'initial' or 'followup'
        )
    ''')
    conn.commit()
    conn.close()

def log_email_to_db(recipient, first_name, company, subject, body_html, message_id, status, error_msg=None, campaign_id="summer_intern_2026", email_type="initial"):
    """Logs the complete email execution and tracking metadata into the DB."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO emails (recipient_email, first_name, company_name, subject, body_html, message_id, status, error_msg, sent_time, campaign_id, email_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (recipient, first_name, company, subject, body_html, message_id, status, error_msg, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), campaign_id, email_type))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")