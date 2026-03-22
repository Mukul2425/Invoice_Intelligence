import imaplib
import email
import os
from datetime import datetime, timedelta
import logging

from config.settings import get_settings
from config.logging_config import setup_logging

logger = logging.getLogger(__name__)


def connect_email():
    settings = get_settings()

    mail = imaplib.IMAP4_SSL(settings.imap_server)
    mail.login(settings.email_address, settings.email_password)
    logger.info("[EMAIL] Connected to IMAP server")
    return mail

def fetch_recent_emails(mail):

    mail.select("inbox")

    since_date = (datetime.now() - timedelta(days=2)).strftime("%d-%b-%Y")

    logger.info("[EMAIL] Searching emails since: %s", since_date)

    status, messages = mail.search(None, 'SINCE', since_date)

    email_ids = messages[0].split()

    logger.info("[EMAIL] Emails found: %s", len(email_ids))

    return email_ids


def save_attachment(file_data, filename):

    today = datetime.now().strftime("%Y-%m")
    folder = f"bills/{today}"

    os.makedirs(folder, exist_ok=True)

    # create unique filename using timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    unique_filename = f"{timestamp}_{filename}"

    filepath = os.path.join(folder, unique_filename)

    with open(filepath, "wb") as f:
        f.write(file_data)

    logger.info("[EMAIL] Saved attachment: %s", filepath)

def process_emails():
    setup_logging()

    mail = connect_email()
    email_ids = fetch_recent_emails(mail)

    try:
        for e_id in email_ids:
            status, msg_data = mail.fetch(e_id, "(RFC822)")

            if status != "OK":
                logger.warning("[EMAIL] Failed to fetch email id: %s", e_id)
                continue

            for response_part in msg_data:
                if isinstance(response_part, tuple):

                    msg = email.message_from_bytes(response_part[1])
                    for part in msg.walk():

                        filename = part.get_filename()
                        allowed_extensions = [".pdf", ".png", ".jpg", ".jpeg"]

                        if filename and any(filename.lower().endswith(ext) for ext in allowed_extensions):

                            file_data = part.get_payload(decode=True)
                            if not file_data:
                                logger.warning("[EMAIL] Empty attachment payload skipped: %s", filename)
                                continue

                            file_size = len(file_data)

                            if file_size < 5000:
                                logger.info("[EMAIL] Skipping small file: %s", filename)
                                continue

                            save_attachment(file_data, filename)
    except Exception as e:
        logger.exception("[EMAIL] Email processing failed: %s", e)
        raise
    finally:
        try:
            mail.logout()
            logger.info("[EMAIL] Logged out from IMAP")
        except Exception:
            logger.warning("[EMAIL] Failed to logout cleanly")

if __name__ == "__main__":
    process_emails()