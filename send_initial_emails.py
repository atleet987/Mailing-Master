import os
import time
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import make_msgid
from dotenv import load_dotenv                  # Loads environment files
from email_utils import init_db, log_email_to_db

# Load configs from .env file securely
load_dotenv()
IITK_EMAIL = os.getenv("IITK_EMAIL")
IITK_PASSWORD = os.getenv("IITK_PASSWORD")

# Initialize database dynamically on script start
init_db()

def build_and_send_email(sender_email, sender_password, recipient_email, first_name, company_name):
    campaign_id = "summer_intern_2026"
    subject = f"IIT Undergrad Interested in Interning at {company_name}"
    resume_link = "https://drive.google.com/file/d/1Y3UYalYI2f5bfryytbRIu8TwJQdbBcE-/view?usp=sharing"

    # Dynamic fallback check for company name presentation
    display_company = f"at <strong>{company_name}</strong>" if company_name else ""

    # HTML Body Design (Optimized with Fixed Width constraints for tightly snap alignment)
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; font-size: 15px; color: #000; line-height: 1.5;">
        <p>Hi {first_name},</p>
        <p>I hope you’re doing well.</p>
        <p>I’m Abhay Tripathi, a third-year undergraduate pursuing a B.Tech in Chemical Engineering at IIT Kanpur. I’m reaching out to inquire about internship opportunities in <strong>Data Science, Machine Learning, Business Analytics or Full-Stack Development</strong> {display_company}.</p>
        <p>I’ve attached my <a href="{resume_link}" target="_blank">resume</a> for your reference and would be happy to provide any additional information if needed.</p>
        <p>Looking forward to hearing from you.</p>
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
                    <p style="margin: 1px 0 0 0;"><a href="mailto:{sender_email}" style="color: #0056b3; text-decoration: none;">{sender_email}</a></p>
                    <p style="margin: 0; color: #222;">Phone: +91 9369555861</p>
                    
                    <p style="margin: 5px 0 0 0; padding: 0; line-height: 1;">
                        <a href="https://www.linkedin.com/in/abhay-tripathi-5733b7293/" style="text-decoration: none; display: inline-block; margin-right: 8px;">
                            <img src="cid:linkedin" width="18" height="18" style="vertical-align: middle; border: 0;">
                        </a>
                        <a href="https://github.com/atleet987" style="text-decoration: none; display: inline-block;">
                            <img src="cid:github" width="18" height="18" style="vertical-align: middle; border: 0;">
                        </a>
                    </p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    # ==============================================================================
    # STRUCTURAL EMAIL ADJUSTMENTS FOR RELIABLE GRAPHICS COHESION
    # ==============================================================================
    message = MIMEMultipart('related')
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject
    
    msg_id = make_msgid(domain='iitk.ac.in')
    message['Message-ID'] = msg_id

    # Alternative text layer nested tightly beneath root
    msg_alternative = MIMEMultipart('alternative')
    message.attach(msg_alternative)
    msg_alternative.attach(MIMEText(body_html, 'html'))

    # Asset processing map pulling explicitly from assets folder
    asset_mapping = [
        ('logo', 'assets/iitk_logo.png'),
        ('linkedin', 'assets/linkedin.png'),
        ('github', 'assets/github.png')
    ]

    for asset_id, filepath in asset_mapping:
        try:
            with open(filepath, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-ID', f'<{asset_id}>')
                img.add_header('Content-Disposition', 'inline', filename=os.path.basename(filepath))
                message.attach(img)
        except FileNotFoundError:
            print(f"Warning: Asset file '{filepath}' missing. Transmission continuing without it.")

    # SMTP Execution Block
    try:
        with smtplib.SMTP('mmtp.iitk.ac.in', 25, timeout=30) as server:
            server.ehlo()
            server.login(sender_email, sender_password)
            server.send_message(message)
            
        print(f" Successfully sent email to {recipient_email}")
        log_email_to_db(recipient_email, first_name, company_name, subject, body_html, msg_id, "SENT", campaign_id=campaign_id)
        return True
    except Exception as e:
        print(f"❌ SMTP Error for {recipient_email}: {e}")
        log_email_to_db(recipient_email, first_name, company_name, subject, body_html, None, "FAILED", error_msg=str(e), campaign_id=campaign_id)
        return False


# Execution Loop
if __name__ == "__main__":
    # Check if configurations were pulled successfully
    if not IITK_EMAIL or not IITK_PASSWORD:
        print("❌ Error: Missing configuration parameters inside '.env'. Verify file setups.")
        exit(1)
        
    sent_count, failed_count = 0, 0

    try:
        with open('mail_check.csv', 'r', newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                recipient = row['Email'].strip() if row.get('Email') else ''
                if not recipient:
                    continue
                
                first_name = row['First name'].strip() if row.get('First name') else ''
                company = row['Company name'].strip() if row.get('Company name') else ''
                
                print(f"Processing target: {recipient} ({company})")
                success = build_and_send_email(IITK_EMAIL, IITK_PASSWORD, recipient, first_name, company)
                
                if success:
                    sent_count += 1
                    time.sleep(10) # 10s Rate-limiting safety interval
                else:
                    failed_count += 1
                    time.sleep(120) # Back-off protection on failures
    except FileNotFoundError:
        print("Error: 'mail_check2.csv' not found. Please place it in the workspace directory.")

    print(f"\nExecution Complete.\nSent: {sent_count} | Failed: {failed_count}")