from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from database.db import Base

class Invoice(Base):

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    vendor_name = Column(String)
    invoice_number = Column(String, unique=True)
    invoice_date = Column(String)
    due_date = Column(String)

    total_amount = Column(Float)
    tax = Column(String)
    payment_status = Column(String)

    file_path = Column(String)
    category = Column(String)

    line_items = relationship("LineItem", back_populates="invoice")

class LineItem(Base):

    __tablename__ = "line_items"

    id = Column(Integer, primary_key=True, index=True)

    invoice_id = Column(Integer, ForeignKey("invoices.id"))

    description = Column(String)
    quantity = Column(String)
    unit_price = Column(String)
    item_total = Column(String)

    invoice = relationship("Invoice", back_populates="line_items")