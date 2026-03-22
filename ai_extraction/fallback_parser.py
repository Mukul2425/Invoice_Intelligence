import re


def _first_match(patterns, text, flags=0):
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            return match.group(1).strip()
    return ""


def _clean_amount(value):
    if not value:
        return ""

    cleaned = value.replace(",", "")
    cleaned = re.sub(r"[^0-9.]", "", cleaned)
    return cleaned.strip()


def _extract_vendor_name(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    noise = ("invoice", "bill to", "ship to", "date", "due", "total", "tax", "amount")

    for line in lines[:8]:
        lower = line.lower()
        if any(token in lower for token in noise):
            continue
        if re.search(r"\d", line):
            continue
        if len(line) >= 3:
            return line

    return ""

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

    data["vendor_name"] = _extract_vendor_name(text)

    data["invoice_number"] = _first_match([
        r"(?im)^\s*invoice\s*(?:no\.?|number|#)?\s*[:\-]?\s*([A-Z0-9\-/]+)",
        r"\b(INV[- ]?\d+)\b",
    ], text)

    data["invoice_date"] = _first_match([
        r"(?im)^\s*(?:invoice\s*)?date\s*[:\-]\s*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
        r"(?im)^\s*(?:invoice\s*)?date\s*[:\-]\s*([A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})",
    ], text)

    data["due_date"] = _first_match([
        r"(?im)^\s*due\s*date\s*[:\-]\s*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})",
        r"(?im)^\s*due\s*date\s*[:\-]\s*([A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})",
    ], text)

    data["tax"] = _clean_amount(_first_match([
        r"(?im)^\s*(?:tax|vat|gst)\s*[:\-]?\s*([$₹€£]?\s*[0-9,]+(?:\.[0-9]{2})?)",
    ], text))

    total_value = _first_match([
        r"(?im)^\s*(?:amount\s*due|total\s*due|grand\s*total|total)\s*[:\-]?\s*([$₹€£]?\s*[0-9,]+(?:\.[0-9]{2})?)",
    ], text)
    if not total_value:
        any_amount = re.findall(r"[$₹€£]?\s*[0-9,]+\.[0-9]{2}", text)
        if any_amount:
            total_value = any_amount[-1]
    data["total_amount"] = _clean_amount(total_value)

    lower_text = text.lower()
    if "overdue" in lower_text:
        data["payment_status"] = "Overdue"
    elif "paid" in lower_text:
        data["payment_status"] = "Paid"
    elif "pending" in lower_text or "unpaid" in lower_text or "amount due" in lower_text:
        data["payment_status"] = "Pending"

    return data

