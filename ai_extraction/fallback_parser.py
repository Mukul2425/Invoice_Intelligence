import re

def regex_fallback(text):

    data = {
        "vendor_name": "",
        "invoice_number": "",
        "invoice_date": "",
        "due_date": "",
        "total_amount": "",
        "tax": "",
        "payment_status": "",
        "line_items": []
    }

    invoice_match = re.search(r"INV[- ]?\d+", text)

    if invoice_match:
        data["invoice_number"] = invoice_match.group()

    total_match = re.search(r"\$?\d+\.\d{2}", text)

    if total_match:
        data["total_amount"] = total_match.group()

    return data

