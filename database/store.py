from database.db import SessionLocal
from database.models import Invoice, LineItem


def save_invoice(data, file_path):

    session = SessionLocal()

    try:

        existing = session.query(Invoice).filter_by(
            invoice_number=data["invoice_number"]
        ).first()

        if existing:
            print("Invoice already exists, skipping")
            return

        invoice = Invoice(

            vendor_name=data["vendor_name"],
            invoice_number=data["invoice_number"],
            invoice_date=data["invoice_date"],
            due_date=data["due_date"],

            total_amount=float(data["total_amount"]) if data["total_amount"] else 0,

            tax=data["tax"],
            payment_status=data["payment_status"],

            file_path=file_path,
            category=""

        )

        session.add(invoice)
        session.commit()

        for item in data["line_items"]:

            line_item = LineItem(

                invoice_id=invoice.id,
                description=item.get("description"),
                quantity=item.get("quantity"),
                unit_price=item.get("unit_price"),
                item_total=item.get("item_total")

            )

            session.add(line_item)

        session.commit()

        print("Invoice stored in database")

    finally:

        session.close()