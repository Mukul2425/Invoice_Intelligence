import os

from email_monitor.email_reader import process_emails
from document_processing.document_reader import read_document
from ai_extraction.extractor import extract_invoice_data

from database.store import save_invoice
from database.db import init_db

from reports.excel_report import generate_report

def setup():

    print("Initializing database...")

    init_db()

def process_invoices():

    folder = "bills"

    for root, dirs, files in os.walk(folder):

        for file in files:

            path = os.path.join(root, file)

            print("\nProcessing invoice:", path)

            try:

                text = read_document(path)

                data = extract_invoice_data(text)

                save_invoice(data, path)

            except Exception as e:

                print("Processing failed:", e)

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