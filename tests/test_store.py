import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.db import Base
from database.models import Invoice, LineItem
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

    @patch("database.store.categorize_invoice", return_value="Other")
    def test_normalizes_dates_amounts_and_status(self, _mock_category):
        data = {
            "vendor_name": "ACME",
            "invoice_number": "INV-3001",
            "invoice_date": "03/22/2026",
            "due_date": "25/03/2026",
            "total_amount": "$1,250.75",
            "tax": "USD 50.25",
            "payment_status": "unpaid",
            "line_items": [
                {"description": "Service", "quantity": "1", "unit_price": "$100.50", "item_total": "$100.50"}
            ],
        }

        with patch("database.store.SessionLocal", self.test_session_local):
            status = save_invoice(data, "bills/2026-03/file_norm.pdf")

            session = self.test_session_local()
            try:
                invoice = session.query(Invoice).filter_by(invoice_number="INV-3001").first()
                item = session.query(LineItem).filter_by(invoice_id=invoice.id).first()
            finally:
                session.close()

        self.assertEqual(status, "stored")
        self.assertEqual(invoice.invoice_date, "2026-03-22")
        self.assertEqual(invoice.due_date, "2026-03-25")
        self.assertEqual(invoice.total_amount, 1250.75)
        self.assertEqual(invoice.tax, "50.25")
        self.assertEqual(invoice.payment_status, "Pending")
        self.assertEqual(item.unit_price, "100.5")
        self.assertEqual(item.item_total, "100.5")


if __name__ == "__main__":
    unittest.main()