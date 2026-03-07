import os
from openpyxl import Workbook
from openpyxl.chart import PieChart, Reference

from database.db import SessionLocal
from database.models import Invoice, LineItem

def fetch_data():

    session = SessionLocal()

    invoices = session.query(Invoice).all()
    line_items = session.query(LineItem).all()

    session.close()

    return invoices, line_items

def generate_report():

    invoices, line_items = fetch_data()

    wb = Workbook()

    ws1 = wb.active
    ws1.title = "Invoices"

    headers = [
        "Vendor",
        "Invoice Number",
        "Invoice Date",
        "Due Date",
        "Total Amount",
        "Category",
        "File Path"
    ]

    ws1.append(headers)

    for inv in invoices:

        ws1.append([
            inv.vendor_name,
            inv.invoice_number,
            inv.invoice_date,
            inv.due_date,
            inv.total_amount,
            inv.category,
            inv.file_path
        ])

    ws2 = wb.create_sheet("Line Items")

    headers = [
        "Invoice ID",
        "Description",
        "Quantity",
        "Unit Price",
        "Item Total"
    ]

    ws2.append(headers)

    for item in line_items:

        ws2.append([
            item.invoice_id,
            item.description,
            item.quantity,
            item.unit_price,
            item.item_total
        ])

    ws3 = wb.create_sheet("Category Summary")
    category_totals = {}

    for inv in invoices:

        category = inv.category if inv.category else "Other"

        if category not in category_totals:
            category_totals[category] = 0

        category_totals[category] += inv.total_amount

        ws3.append(["Category", "Total Spend"])

    for category, total in category_totals.items():

        ws3.append([category, total])

        chart = PieChart()

    data = Reference(
        ws3,
        min_col=2,
        min_row=1,
        max_row=len(category_totals) + 1
    )

    labels = Reference(
        ws3,
        min_col=1,
        min_row=2,
        max_row=len(category_totals) + 1
    )

    chart.add_data(data, titles_from_data=True)
    chart.set_categories(labels)

    chart.title = "Spend by Category"

    ws3.add_chart(chart, "E5")
    os.makedirs("output", exist_ok=True)

    file_path = "output/expense_report.xlsx"

    wb.save(file_path)

    print("Excel report generated:", file_path)

if __name__ == "__main__":

    generate_report()