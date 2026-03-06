import imaplib
import email
import os
from datetime import datetime
from dotenv import load_dotenv
import logging

logging.basicConfig(
    filename="logs/processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)
load_dotenv()

EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")

IMAP_SERVER = "imap.gmail.com"


def connect_email():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    return mail

from datetime import datetime, timedelta

from datetime import datetime, timedelta

def fetch_recent_emails(mail):

    mail.select("inbox")

    since_date = (datetime.now() - timedelta(days=2)).strftime("%d-%b-%Y")

    print("Searching emails since:", since_date)

    status, messages = mail.search(None, 'SINCE', since_date)

    email_ids = messages[0].split()

    print("Emails found:", len(email_ids))

    return email_ids

def save_attachment(file_data, filename):

    today = datetime.now().strftime("%Y-%m")
    folder = f"bills/{today}"

    os.makedirs(folder, exist_ok=True)

    filepath = os.path.join(folder, filename)

    if os.path.exists(filepath):
        print(f"File already exists, skipping: {filename}")
        return

    with open(filepath, "wb") as f:
        f.write(file_data)

    print(f"Saved attachment: {filepath}")

def process_emails():
    mail = connect_email()
    email_ids = fetch_recent_emails(mail)

    for e_id in email_ids:
        status, msg_data = mail.fetch(e_id, "(RFC822)")

        for response_part in msg_data:
            if isinstance(response_part, tuple):

                msg = email.message_from_bytes(response_part[1])
                for part in msg.walk():

                    filename = part.get_filename()
                    allowed_extensions = [".pdf", ".png", ".jpg", ".jpeg"]

                    if filename and any(filename.lower().endswith(ext) for ext in allowed_extensions):

                        file_data = part.get_payload(decode=True)
                        file_size = len(file_data)

                        if file_size < 5000:
                            print("Skipping small file:", filename)
                            continue

                        save_attachment(file_data, filename)

if __name__ == "__main__":
    process_emails()