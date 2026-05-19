import os
import sqlite3
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

# Determine the absolute directory where dashboard.py lives
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_NAME = os.path.join(BASE_DIR, "emails.db")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    # 1. Fetch all emails chronologically to render table rows
    emails_rows = query_db("SELECT id, recipient_email, company_name, subject, status, sent_time, email_type FROM emails ORDER BY id DESC")
    emails = [dict(row) for row in emails_rows]
    
    # 2. Build a mapping tracker to find the absolute latest stage for each user
    # This prevents an email address from showing up in Stage 1 if they have already progressed to Stage 2
    latest_stage_map = {}
    
    # Scan chronologically (oldest to newest) so later stages overwrite earlier ones
    for email in reversed(emails):
        if email['status'] == 'SENT':
            email_type = email['email_type']
            # We track 'initial' and specific 'followup_X' stages
            latest_stage_map[email['recipient_email']] = email_type

    # 3. Inject the latest stage property into every email dictionary object
    for email in emails:
        email['latest_active_stage'] = latest_stage_map.get(email['recipient_email'], email['email_type'])
        
    return render_template('index.html', emails=emails)

@app.route('/email/<int:email_id>')
def preview(email_id):
    # 1. Fetch the clicked email row
    current_email = query_db("SELECT * FROM emails WHERE id = ?", [email_id], one=True)
    if not current_email:
        return "Record missing", 404
    
    current_email = dict(current_email)
    
    # 2. Reconstruct the historical thread
    thread_history = []
    
    # If this is a follow-up, find all prior messages exchanged with this specific recipient
    if current_email['email_type'] != 'initial' and current_email['message_id']:
        # Fetch older successful emails to the same recipient, sorted chronologically
        prior_emails = query_db(
            "SELECT body_html, sent_time, subject, email_type FROM emails WHERE recipient_email = ? AND id < ? AND status = 'SENT' ORDER BY id DESC",
            [current_email['recipient_email'], email_id]
        )
        for old_mail in prior_emails:
            old_mail_dict = dict(old_mail)
            # Process static asset mapping for old items
            old_html = old_mail_dict['body_html']
            old_html = old_html.replace('cid:logo', '/assets/iitk_logo.png')
            old_html = old_html.replace('cid:linkedin', '/assets/linkedin.png')
            old_html = old_html.replace('cid:github', '/assets/github.png')
            old_mail_dict['body_html'] = old_html
            thread_history.append(old_mail_dict)

    # 3. Process static asset mapping for the main/top message
    raw_html = current_email['body_html']
    raw_html = raw_html.replace('cid:logo', '/assets/iitk_logo.png')
    raw_html = raw_html.replace('cid:linkedin', '/assets/linkedin.png')
    raw_html = raw_html.replace('cid:github', '/assets/github.png')
    current_email['body_html'] = raw_html
    
    return render_template('preview.html', email=current_email, thread_history=thread_history)

# Explicitly routing and serving files from the absolute assets directory path
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(ASSETS_DIR, filename)

if __name__ == "__main__":
    print(f"\nTarget Assets Directory: {ASSETS_DIR}")
    print("Starting local server on http://127.0.0.1:5000 \n")
    app.run(debug=True, port=5000)