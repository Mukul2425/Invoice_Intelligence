import imaplib
import email
import os
from datetime import datetime, timedelta
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config.settings import get_settings
from config.logging_config import setup_logging

logger = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(get_settings().imap_retry_attempts),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type((imaplib.IMAP4.error, OSError, TimeoutError, RuntimeError)),
    reraise=True,
)
def _connect_email_with_retry(settings):
    mail = imaplib.IMAP4_SSL(settings.imap_server, timeout=settings.imap_timeout_seconds)
    mail.login(settings.email_address, settings.email_password)
    return mail


def connect_email():
    settings = get_settings()

    mail = _connect_email_with_retry(settings)
    logger.info("[EMAIL] Connected to IMAP server")
    return mail


@retry(
    stop=stop_after_attempt(get_settings().imap_retry_attempts),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type((imaplib.IMAP4.error, OSError, TimeoutError, RuntimeError)),
    reraise=True,
)
def _search_recent_email_ids(mail, since_date):
    mail.select("inbox")
    status, messages = mail.search(None, "SINCE", since_date)

    if status != "OK":
        raise RuntimeError("IMAP search failed")

    return messages[0].split()

def fetch_recent_emails(mail):
    since_date = (datetime.now() - timedelta(days=2)).strftime("%d-%b-%Y")

    logger.info("[EMAIL] Searching emails since: %s", since_date)

    email_ids = _search_recent_email_ids(mail, since_date)

    logger.info("[EMAIL] Emails found: %s", len(email_ids))

    return email_ids


@retry(
    stop=stop_after_attempt(get_settings().imap_retry_attempts),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type((imaplib.IMAP4.error, OSError, TimeoutError, RuntimeError)),
    reraise=True,
)
def _fetch_email(mail, email_id):
    status, msg_data = mail.fetch(email_id, "(RFC822)")
    if status != "OK":
        raise RuntimeError(f"Failed to fetch email id: {email_id}")
    return msg_data


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
            try:
                msg_data = _fetch_email(mail, e_id)
            except Exception as fetch_error:
                logger.warning("[EMAIL] Skipping email id after retries %s: %s", e_id, fetch_error)
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