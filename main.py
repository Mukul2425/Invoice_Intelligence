import logging
import os

from ai_extraction.extractor import extract_invoice_data
from config.logging_config import setup_logging
from config.settings import validate_startup_settings
from database.db import init_db
from database.processing_state import mark_file_processed, should_process_file
from database.store import save_invoice
from document_processing.document_reader import read_document
from email_monitor.email_reader import process_emails
from reports.excel_report import generate_report

logger = logging.getLogger(__name__)


def setup():

    setup_logging()

    validate_startup_settings()

    logger.info("[SETUP] Initializing database")

    init_db()


def process_invoices():

    folder = "bills"

    processed = 0
    stored = 0
    skipped = 0

    for root, dirs, files in os.walk(folder):

        for file in files:

            path = os.path.join(root, file)

            try:
                if not should_process_file(path):
                    logger.info("[PIPELINE] Skipping unchanged file: %s", path)
                    skipped += 1
                    continue

                logger.info("[PIPELINE] Processing invoice: %s", path)

                processed += 1

                text = read_document(path)

                data = extract_invoice_data(text)

                status = save_invoice(data, path)

                if status == "stored":
                    stored += 1
                    mark_file_processed(path, status)
                elif status == "duplicate":
                    skipped += 1
                    mark_file_processed(path, status)

            except Exception as e:
                logger.exception("[PIPELINE] Processing failed for %s: %s", path, e)

    logger.info("[PIPELINE] ----- Processing Summary -----")
    logger.info("[PIPELINE] Invoices processed: %s", processed)
    logger.info("[PIPELINE] New invoices stored: %s", stored)
    logger.info("[PIPELINE] Duplicates skipped: %s", skipped)


def main():

    setup()

    logger.info("[PIPELINE] ----- Invoice Intelligence Pipeline -----")

    logger.info("[EMAIL] Checking email for invoices")
    process_emails()

    logger.info("[PIPELINE] Processing downloaded invoices")
    process_invoices()

    logger.info("[REPORT] Generating expense report")
    generate_report()

    logger.info("[PIPELINE] Pipeline completed successfully")


if __name__ == "__main__":

    main()
