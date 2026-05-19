import os
import time
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import make_msgid
from dotenv import load_dotenv
from email_utils import log_email_to_db

load_dotenv()
IITK_EMAIL = os.getenv("IITK_EMAIL")
IITK_PASSWORD = os.getenv("IITK_PASSWORD")
DB_NAME = "emails.db"

# ==============================================================================
# 📝 DEFINE YOUR CONTENT TEMPLATES HERE
# ==============================================================================
STAGE_TEMPLATES = {
    1: {
        "subject_prefix": "Re: ",
        "body": lambda name, comp: f"<p>Hi {name},</p><p>I wanted to follow up briefly on my previous email regarding internship opportunities at <strong>{comp}</strong>. I know things get incredibly busy, so I wanted to bring my application back to the top of your inbox.</p>"
    },
    2: {
        "subject_prefix": "Re: ",
        "body": lambda name, comp: f"<p>Hi {name},</p><p>Hoping for a response from you soon.</p>"
    }
}

def fetch_targets_for_stage(stage_number):
    """Dynamically finds the correct parent message based on targeted stage."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # If looking to send stage 1, look for successful 'initial' emails
    # If looking to send stage 2, look for successful 'followup_1' emails
    parent_type = "initial" if stage_number == 1 else f"followup_{stage_number - 1}"
    current_type = f"followup_{stage_number}"
    
    query = f"""
        SELECT * FROM emails p
        WHERE p.status = 'SENT' 
          AND p.email_type = '{parent_type}'
          AND NOT EXISTS (
              SELECT 1 FROM emails c 
              WHERE c.recipient_email = p.recipient_email 
                AND c.email_type = '{current_type}'
          )
    """
    cursor.execute(query)
    records = cursor.fetchall()
    conn.close()
    return records

def execute_followup_campaign(stage):
    if stage not in STAGE_TEMPLATES:
        print(f"❌ Error: Stage {stage} is not configured in STAGE_TEMPLATES.")
        return

    targets = fetch_targets_for_stage(stage)
    if not targets:
        print(f"No pending targets found qualified for Stage {stage} follow-ups.")
        return
        
    print(f"Found {len(targets)} entries qualified to receive Follow-up Stage {stage}.\n")
    
    for row in targets:
        recipient = row['recipient_email']
        first_name = row['first_name']
        company = row['company_name']
        parent_msg_id = row['message_id']
        
        # Build threaded subject and dynamic body content
        clean_subject = row['subject'].replace("Re: ", "").replace("Final Follow-up: ", "")
        subject = f"{STAGE_TEMPLATES[stage]['subject_prefix']}{clean_subject}"
        
        inner_message = STAGE_TEMPLATES[stage]['body'](first_name, company)
        
        # Complete HTML with your standard responsive signature block
        body_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; font-size: 15px; color: #000; line-height: 1.5;">
            {inner_message}
            <p>Best regards,</p>
            <table style="font-family: Arial, sans-serif; font-size: 14px; color: #000; margin-top: 12px; border-collapse: collapse; width: 450px;">
                <tr>
                    <td style="vertical-align: top; width: 105px; padding-right: 15px; padding-top: 2px;">
                        <img src="cid:logo" width="105" style="display: block; border: 0; width: 105px;">
                    </td>
                    <td style="vertical-align: top; line-height: 1.35;">
                        <p style="margin: 0; font-weight: bold; font-size: 16px; color: #000;">Abhay Tripathi</p>
                        <p style="margin: 1px 0 0 0; color: #222;">Third-Year Undergraduate</p>
                        <p style="margin: 0; color: #222;">B.Tech in Chemical Engineering</p>
                        <p style="margin: 0; color: #222;">Indian Institute of Technology, Kanpur</p>
                        <p style="margin: 1px 0 0 0;"><a href="mailto:{IITK_EMAIL}" style="color: #0056b3; text-decoration: none;">{IITK_EMAIL}</a></p>
                        <p style="margin: 0; color: #222;">Phone: +91 9369555861</p>
                        <p style="margin: 5px 0 0 0; padding: 0; line-height: 1;">
                            <a href="https://www.linkedin.com/in/abhay-tripathi-5733b7293/"><img src="cid:linkedin" width="18" height="18" style="vertical-align: middle; border: 0; margin-right: 8px;"></a>
                            <a href="https://github.com/atleet987"><img src="cid:github" width="18" height="18" style="vertical-align: middle; border: 0;"></a>
                        </p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        message = MIMEMultipart('related')
        message['From'] = IITK_EMAIL
        message['To'] = recipient
        message['Subject'] = subject
        
        new_msg_id = make_msgid(domain='iitk.ac.in')
        message['Message-ID'] = new_msg_id
        message['In-Reply-To'] = parent_msg_id
        message['References'] = parent_msg_id

        msg_alternative = MIMEMultipart('alternative')
        message.attach(msg_alternative)
        msg_alternative.attach(MIMEText(body_html, 'html'))

        # Standard Asset attachment engine
        for asset_id, path in [('logo', 'assets/iitk_logo.png'), ('linkedin', 'assets/linkedin.png'), ('github', 'assets/github.png')]:
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-ID', f'<{asset_id}>')
                    img.add_header('Content-Disposition', 'inline', filename=os.path.basename(path))
                    message.attach(img)

        try:
            with smtplib.SMTP('mmtp.iitk.ac.in', 25, timeout=30) as server:
                server.ehlo()
                server.login(IITK_EMAIL, IITK_PASSWORD)
                server.send_message(message)
            print(f"✅ Dispatched Stage {stage} Follow-up to: {recipient}")
            log_email_to_db(recipient, first_name, company, subject, body_html, new_msg_id, "SENT", email_type=f"followup_{stage}")
            time.sleep(10)
        except Exception as e:
            print(f"❌ Failed processing {recipient}: {e}")
            log_email_to_db(recipient, first_name, company, subject, body_html, None, "FAILED", error_msg=str(e), email_type=f"followup_{stage}")
            time.sleep(120)

if __name__ == "__main__":
    # CHANGE THIS NUMBER DEPENDING ON WHICH STAGE YOU WANT TO EXECUTE
    TARGET_STAGE = 1
    
    print(f"--- Launching Follow-up Sequence Engine for Stage {TARGET_STAGE} ---")
    execute_followup_campaign(TARGET_STAGE)