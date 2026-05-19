# ✈️ IITK Cold Mailing Master

A lightweight, local Mail Automation platform engineered specifically to manage bulk internship outreach and automated programmatic follow-up sequences natively through the **IIT Kanpur SMTP mail relay (`mmtp.iitk.ac.in`)**.

Instead of relying on fragile IMAP synchronization tools, this architecture uses a local **SQLite database core** to record precise transactional logs, generate immutable HTML browser previews, and manage state-driven follow-up threads using standard network headers (`In-Reply-To` and `References`).

---

## 🏗️ System Architecture & Workflow

1. **Main Engine (`send_initial_emails.py`)**: Parses your customized CSV payload list, builds responsive multi-part MIME configurations with compressed inline image signatures, dispatches data safely through IITK servers under local rate limits, and registers thread anchors in the DB.
2. **State Management (`email_utils.py` & `emails.db`)**: Centralized local relational engine tracking communication logs, errors, execution timestamps, and progression stages.
3. **Sequence Automation (`send_followups.py`)**: Reads the operational state from the database. It isolates recipients who haven't progressed, looks up past `Message-ID` nodes, and appends perfectly nested reply strings directly onto existing threads in the recruiter's inbox.
4. **Dashboard (`dashboard.py`)**: A local web interface built with **Flask** that separates active initial outbounds and follow-up stages into isolated monitoring panels with an interactive conversational layout.

---

## 📁 Directory Structure

```text
iitk_outreach_system/
│
├── send_initial_emails.py   # Core introductory outbound campaign manager
├── send_followups.py        # Automated programmatic follow-up sequence engine
├── dashboard.py             # Flask-powered tracking database dashboard UI
├── email_utils.py           # Relational schema initialization and log adapters
├── .env                     # Local hidden environment configurations (Git ignored)
├── mail_check.csv           # CSV file containing email of the User (for testing purpose)
├── emails.db                # Auto-generated SQLite data warehouse
│
├── templates/               # Client-side UI markup folder
│   ├── base.html
│   ├── index.html
│   └── preview.html
│
└── assets/                  # High-performance local graphic attachment directory
    ├── iitk_logo.png
    ├── linkedin.png
    └── github.png
```
---

## 🏃‍♂️ Step-by-Step Execution Guide

Follow this sequential workflow to configure your workspace environment, manage network access constraints, and execute your multi-stage outreach campaigns:

1. **Configure Environment Secrets (`.env`)** Create a configuration file named strictly `.env` in the root directory of the project. Populate it with your authentic campus mail parameters:
   ```env
   IITK_EMAIL=your_username@iitk.ac.in
   IITK_PASSWORD=your_secret_campus_password

2. **Connect to the Institute VPN:** Because the secure SMTP server (mmtp.iitk.ac.in) operates entirely within the protected university network infrastructure, you must be connected to the campus intranet. If you are operating off-campus, you must successfully initialize and connect to the IITK Institute VPN (via FortiClient or your preferred configuration profile) before executing any script.

3. **Prepare Recipient Dataset:** Save a CSV file in the project root directory that contains the data of the email recipients in the exact format shown in the testing profile `mail_check.csv`.

4. **Verify File Pointers in Script:** Open `send_initial_emails.py` in your code editor. In the open() file block near the bottom of the script, ensure you are using the exact filename of the file containing your target recipient data:
```python
with open('mail_check.csv', 'r', newline='', encoding='utf-8-sig') as file:
```

5. **Launch Primary Outreach (Day 0 Campaign):** Open your terminal window inside the root folder and run the execution command to send your first wave of emails:
```python send_initial_emails.py```
The application will read your CSV file row-by-row, automatically initialize your tracking database (emails.db), and dispatch your high-resolution HTML emails across safe 10-second cooling intervals.

6. **Execute Stage-1 Follow-Ups:** When you are ready to send your first round of reminders, open `send_followups.py`, navigate to the bottom execution block, and ensure the command is used with TARGET_STAGE = 1:
```python
if __name__ == "__main__": TARGET_STAGE = 1  # Sets tracking bounds to process Stage 1 Follow-ups
```
Run the sequence tool directly from your terminal:
```terminal
python send_followups.py
```

7. **Execute Stage 2 Follow-Ups and Beyond:** To send your second round of reminders to contacts who received Follow-Up 1 but have still not replied, open send_followups.py and ensure the command is used with TARGET_STAGE = 2:
```python
if __name__ == "__main__":
    TARGET_STAGE = 2  # Moves target criteria to Stage 2 Follow-ups
```
Execute the same command in your terminal window:
```terminal 
python send_followups.py
```
(You can scale this sequentially to Stage 3 and beyond by changing this target integer and defining matching template strings in the code structure).

8. **Initialize the Email Tracking Dashboard:** The command python `dashboard.py` runs the dashboard, which shows the real-time status of the emails across your various operational levels:
```terminal
python dashboard.py
```
Once initialized, open your web browser and navigate to `http://127.0.0.1:5000`. The dashboard divides your outbound metrics into isolated main panels and distinct sub-tabs, categorizing contacts strictly by their last active conversation step (Initial Email, First Followup, Second Followup...) to keep your pipeline clean.
