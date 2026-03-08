import os

from email_monitor.email_reader import process_emails
from document_processing.document_reader import read_document
from ai_extraction.extractor import extract_invoice_data

from database.store import save_invoice
from database.db import init_db, SessionLocal
from database.models import Invoice

from reports.excel_report import generate_report


def setup():

    print("Initializing database...")

    init_db()


def process_invoices():

    folder = "bills"

    processed = 0
    stored = 0
    skipped = 0

    for root, dirs, files in os.walk(folder):

        for file in files:

            path = os.path.join(root, file)

            session = SessionLocal()

            try:

                existing = session.query(Invoice).filter_by(file_path=path).first()

                if existing:
                    print("Invoice already processed:", path)
                    skipped += 1
                    continue

                print("\nProcessing invoice:", path)

                processed += 1

                text = read_document(path)

                data = extract_invoice_data(text)

                save_invoice(data, path)

                stored += 1

            except Exception as e:

                print("Processing failed:", e)

            finally:

                session.close()

    print("\n----- Processing Summary -----")
    print(f"Invoices processed: {processed}")
    print(f"New invoices stored: {stored}")
    print(f"Duplicates skipped: {skipped}")


def main():

    print("\n----- Invoice Intelligence Pipeline -----\n")

    setup()

    print("\nChecking email for invoices...\n")
    process_emails()

    print("\nProcessing downloaded invoices...\n")
    process_invoices()

    print("\nGenerating expense report...\n")
    generate_report()

    print("\nPipeline completed successfully.\n")


if __name__ == "__main__":

    main()