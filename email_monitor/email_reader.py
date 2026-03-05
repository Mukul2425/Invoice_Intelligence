import imaplib
import email
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")

IMAP_SERVER = "imap.gmail.com"


def connect_email():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    return mail

def fetch_unread_emails(mail):
    mail.select("inbox")
    status, messages = mail.search(None, '(UNSEEN)')
    email_ids = messages[0].split()
    return email_ids

def save_attachment(part, filename):
    today = datetime.now().strftime("%Y-%m")
    folder = f"bills/{today}"

    os.makedirs(folder, exist_ok=True)

    filepath = os.path.join(folder, filename)

    with open(filepath, "wb") as f:
        f.write(part.get_payload(decode=True))

    print(f"Saved attachment: {filepath}")

def process_emails():
    mail = connect_email()
    email_ids = fetch_unread_emails(mail)

    for e_id in email_ids:
        status, msg_data = mail.fetch(e_id, "(RFC822)")

        for response_part in msg_data:
            if isinstance(response_part, tuple):

                msg = email.message_from_bytes(response_part[1])

                for part in msg.walk():

                    if part.get_content_disposition() == "attachment":
                        filename = part.get_filename()

                        if filename:
                            save_attachment(part, filename)

if __name__ == "__main__":
    process_emails()