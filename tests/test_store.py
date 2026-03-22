import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.db import Base
from database.store import save_invoice


def _sample_data(invoice_number="INV-1001"):
    return {
        "vendor_name": "ACME",
        "invoice_number": invoice_number,
        "invoice_date": "2026-03-21",
        "due_date": "2026-03-30",
        "total_amount": "100.00",
        "tax": "0",
        "payment_status": "pending",
        "line_items": [],
    }


class TestStoreSaveInvoice(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:")
        self.test_session_local = sessionmaker(bind=engine)
        Base.metadata.create_all(bind=engine)

    @patch("database.store.categorize_invoice", return_value="Other")
    def test_save_and_duplicate_by_invoice_number(self, _mock_category):
        with patch("database.store.SessionLocal", self.test_session_local):
            status_first = save_invoice(_sample_data("INV-2001"), "bills/2026-03/file_a.pdf")
            status_second = save_invoice(_sample_data("INV-2001"), "bills/2026-03/file_b.pdf")

        self.assertEqual(status_first, "stored")
        self.assertEqual(status_second, "duplicate")

    @patch("database.store.categorize_invoice", return_value="Other")
    def test_duplicate_by_file_path_when_invoice_number_missing(self, _mock_category):
        with patch("database.store.SessionLocal", self.test_session_local):
            data = _sample_data(invoice_number="")
            status_first = save_invoice(data, "bills/2026-03/file_same.pdf")
            status_second = save_invoice(data, "bills/2026-03/file_same.pdf")

        self.assertEqual(status_first, "stored")
        self.assertEqual(status_second, "duplicate")


if __name__ == "__main__":
    unittest.main()