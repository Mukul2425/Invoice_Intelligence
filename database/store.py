import logging
import re
from datetime import datetime

from categorization.categorize import categorize_invoice
from database.db import SessionLocal
from database.models import Invoice, LineItem

logger = logging.getLogger(__name__)


def _normalize_amount(value, default=0.0):
    if value is None:
        return default

    cleaned = re.sub(r"[^0-9.-]", "", str(value).replace(",", ""))
    if cleaned in {"", ".", "-", "-."}:
        return default

    try:
        return float(cleaned)
    except ValueError:
        return default


def _normalize_date(value):
    if not value:
        return ""

    text = str(value).strip()
    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d/%m/%y",
        "%m/%d/%y",
        "%b %d, %Y",
        "%B %d, %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return text


def _normalize_payment_status(value):
    lowered = (value or "").strip().lower()

    if lowered in {"paid", "complete", "completed", "settled"}:
        return "Paid"
    if lowered in {"overdue", "late"}:
        return "Overdue"
    if lowered in {"pending", "unpaid", "due", "open"}:
        return "Pending"
    return ""


def _is_duplicate_invoice(session, data, file_path):

    invoice_number = (data.get("invoice_number") or "").strip()

    if invoice_number:
        existing = session.query(Invoice).filter_by(invoice_number=invoice_number).first()
        if existing:
            return True

    existing_file = session.query(Invoice).filter_by(file_path=file_path).first()
    if existing_file:
        return True

    return False


def save_invoice(data, file_path):

    session = SessionLocal()

    vendor = data.get("vendor_name", "")
    category = categorize_invoice(vendor)

    try:

        if _is_duplicate_invoice(session, data, file_path):
            logger.info("[DB] Invoice already exists, skipping: %s", file_path)
            return "duplicate"

        invoice_number = (data.get("invoice_number") or "").strip() or None

        invoice = Invoice(

            vendor_name=vendor,
            invoice_number=invoice_number,
            invoice_date=_normalize_date(data.get("invoice_date", "")),
            due_date=_normalize_date(data.get("due_date", "")),

            total_amount=_normalize_amount(data.get("total_amount"), default=0.0),

            tax=str(_normalize_amount(data.get("tax", ""), default=0.0)),
            payment_status=_normalize_payment_status(data.get("payment_status", "")),

            file_path=file_path,
            category=category
        )

        session.add(invoice)
        session.commit()

        for item in data.get("line_items", []):

            line_item = LineItem(

                invoice_id=invoice.id,
                description=item.get("description"),
                quantity=item.get("quantity"),
                unit_price=str(_normalize_amount(item.get("unit_price"), default=0.0)),
                item_total=str(_normalize_amount(item.get("item_total"), default=0.0))

            )

            session.add(line_item)

        session.commit()

        logger.info("[DB] Invoice stored in database: %s", file_path)
        return "stored"

    except Exception as e:

        session.rollback()
        logger.exception("[DB] Database error for %s: %s", file_path, e)
        return "error"

    finally:

        session.close()
