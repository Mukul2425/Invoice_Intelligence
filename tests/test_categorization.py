import unittest
from unittest.mock import patch

from categorization.categorize import categorize_invoice, rule_based_category


class TestCategorization(unittest.TestCase):
    def test_rule_based_category_match(self):
        self.assertEqual(rule_based_category("Amazon Web Services"), "Tools & Software")

    def test_empty_vendor_defaults_to_other(self):
        self.assertEqual(categorize_invoice(""), "Other")

    @patch("categorization.categorize.llm_category", return_value="Utilities")
    def test_llm_used_when_rule_misses(self, _mock_llm):
        self.assertEqual(categorize_invoice("Unknown Vendor"), "Utilities")

    @patch("categorization.categorize.llm_category", return_value="tools and software")
    def test_llm_output_is_normalized_to_allowed_category(self, _mock_llm):
        self.assertEqual(categorize_invoice("Custom SaaS Vendor"), "Tools & Software")

    @patch("categorization.categorize.llm_category", return_value="Random Category")
    def test_unknown_llm_output_defaults_to_other(self, _mock_llm):
        self.assertEqual(categorize_invoice("Unknown Vendor"), "Other")


if __name__ == "__main__":
    unittest.main()
