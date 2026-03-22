import logging

from database.db import SessionLocal
from database.models import Invoice, LineItem
from categorization.categorize import categorize_invoice

logger = logging.getLogger(__name__)


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
            invoice_date=data.get("invoice_date", ""),
            due_date=data.get("due_date", ""),

            total_amount=float(data.get("total_amount")) if data.get("total_amount") else 0,

            tax=data.get("tax", ""),
            payment_status=data.get("payment_status", ""),

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
                unit_price=item.get("unit_price"),
                item_total=item.get("item_total")

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