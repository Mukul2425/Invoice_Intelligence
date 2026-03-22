import unittest

from ai_extraction.fallback_parser import regex_fallback


class TestFallbackParser(unittest.TestCase):
    def test_extracts_invoice_number_and_total(self):
        text = """
        ACME Corp
        Invoice: INV-2026
        Total Due: $123.45
        """

        data = regex_fallback(text)

        self.assertEqual(data["invoice_number"], "INV-2026")
        self.assertEqual(data["total_amount"], "123.45")

    def test_extracts_vendor_dates_tax_and_status(self):
        text = """
        Blue Ocean Supplies
        Invoice Number: BO-7781
        Date: 03/22/2026
        Due Date: 03/29/2026
        Tax: $7.50
        Grand Total: $157.50
        Amount Due
        """

        data = regex_fallback(text)

        self.assertEqual(data["vendor_name"], "Blue Ocean Supplies")
        self.assertEqual(data["invoice_number"], "BO-7781")
        self.assertEqual(data["invoice_date"], "03/22/2026")
        self.assertEqual(data["due_date"], "03/29/2026")
        self.assertEqual(data["tax"], "7.50")
        self.assertEqual(data["total_amount"], "157.50")
        self.assertEqual(data["payment_status"], "Pending")


if __name__ == "__main__":
    unittest.main()
