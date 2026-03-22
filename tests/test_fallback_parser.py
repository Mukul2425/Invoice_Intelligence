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
        self.assertEqual(data["total_amount"], "$123.45")


if __name__ == "__main__":
    unittest.main()