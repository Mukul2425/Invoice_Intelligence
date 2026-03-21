# Finance Automation — Bill & Invoice Intelligence

**Task Chosen:** Task 01 — Finance Automation: Bill & Invoice Intelligence

This project implements a fully automated invoice processing pipeline that monitors an email inbox, downloads invoice attachments, extracts structured financial data using AI and OCR, stores the results in a relational database, and generates an analytics-ready Excel expense report.

The goal is to eliminate manual invoice logging and enable automatic financial tracking across vendors and invoice formats.

---

## Why I Chose This Task

I selected Task 01 — Finance Automation because it combines several real-world engineering challenges:

- Document processing and OCR
- AI-driven data extraction from unstructured text
- Data pipeline automation
- Structured data storage
- Business analytics reporting

This task allowed me to build a complete production-style automation pipeline, integrating AI with traditional software engineering components.

---

## System Architecture

The system follows a modular document-processing pipeline.

```
Email Inbox
     │
     ▼
Email Monitor (IMAP)
     │
     ▼
Attachment Downloader
     │
     ▼
Document Processor
(PDF Reader / OCR)
     │
     ▼
AI Extraction Engine
(Gemini + Regex Fallback)
     │
     ▼
Expense Categorization
(Rule-based + AI)
     │
     ▼
SQLite Database Storage
     │
     ▼
Excel Analytics Report
(Charts + Summary)
```

---

## How the System Works

### 1. Email Monitoring

The system connects to an email inbox using IMAP and detects new emails containing invoice attachments.

**Supported formats:**

- PDF invoices
- Scanned documents
- Image receipts (PNG/JPG)

Attachments are automatically downloaded into a structured directory:

`bills/YYYY-MM/`

### 2. Document Processing

Invoices can arrive in many formats, so the system intelligently processes them:

| Document Type | Method |
|--------------|--------|
| Digital PDFs | Text extraction using PyMuPDF |
| Scanned PDFs | OCR using Tesseract |
| Images | OCR using Tesseract |

The result is normalized invoice text.

### 3. AI Data Extraction

The extracted text is sent to Google Gemini for structured data extraction.

**The AI extracts:**

- Vendor name
- Invoice number
- Invoice date
- Due date
- Total amount
- Tax
- Payment status
- Line items

To ensure reliability, the system includes a regex fallback parser if the LLM response fails.

### 4. Expense Categorization

Each invoice is automatically categorized into:

- Office Expenses
- Tools & Software
- Travel & Petrol
- Utilities
- Other

Categorization uses a hybrid approach:

- Rule-based classification
- LLM classification fallback

### 5. Database Storage

All extracted data is stored in SQLite using SQLAlchemy.

**Database structure:**

#### Invoices Table

| Field | Description |
|-------|-------------|
| vendor_name | Vendor issuing invoice |
| invoice_number | Unique invoice identifier |
| invoice_date | Invoice date |
| due_date | Payment due date |
| total_amount | Invoice total |
| category | Expense category |
| file_path | Stored invoice location |

#### Line Items Table

| Field | Description |
|-------|-------------|
| invoice_id | Foreign key |
| description | Item description |
| quantity | Quantity |
| unit_price | Unit cost |
| item_total | Item total |

### 6. Analytics Report Generation

The system generates an Excel report containing:

- **Sheet 1 — Invoices**
  - All extracted invoices and their metadata.
- **Sheet 2 — Line Items**
  - Detailed invoice itemization.
- **Sheet 3 — Category Summary**
  - Total spend grouped by expense category.

A pie chart visualizes spending distribution across categories.

---

## Initiative Features (Beyond Assignment Requirements)

The system includes several improvements beyond the basic requirements:

- **Hybrid AI Extraction** – LLM extraction with regex fallback ensures robustness when AI output is malformed.
- **Hybrid Expense Categorization** – Rule-based + AI classification minimizes API usage while maintaining flexibility.
- **Duplicate Invoice Protection** – Invoices are skipped if already processed.
- **Unique File Naming** – Attachments are stored with timestamp prefixes to avoid filename collisions.
- **Intelligent Pipeline Processing** – Invoices already processed are skipped automatically.
- **Processing Summary** – The system prints a pipeline execution summary:
  - Invoices processed: X
  - New invoices stored: Y
  - Duplicates skipped: Z
- **Structured Logging** – Processing events are recorded in:
  - `logs/processing.log`

---

## Tech Stack

**Language:** Python

**AI:** Google Gemini API

**Document Processing:** PyMuPDF, Tesseract OCR, pdf2image

**Database:** SQLite + SQLAlchemy

**Reporting:** OpenPyXL

---

## Project Structure

```
invoice-intelligence/
│
├── main.py
├── requirements.txt
├── .env.example
├── README.md
├── Project_Readme.md
│
├── email_monitor/
│   └── email_reader.py
│
├── document_processing/
│   └── document_reader.py
│
├── ai_extraction/
│   ├── extractor.py
│   └── fallback_parser.py
│
├── categorization/
│   └── categorize.py
│
├── database/
│   ├── db.py
│   ├── models.py
│   └── store.py
│
├── reports/
│   └── excel_report.py
│
├── bills/
├── output/
└── logs/
```

---

## Setup Instructions

### 1 Install Dependencies

```bash
pip install -r requirements.txt
```

### 2 Install Tesseract OCR (Mac)

```bash
brew install tesseract
```

### 3 Install Poppler (required for pdf2image) (Mac)

```bash
brew install poppler
```

### 4 Configure Environment Variables

```bash
cp .env.example .env
```

Fill in the variables:

```bash
EMAIL_ADDRESS=
EMAIL_PASSWORD=
GEMINI_API_KEY=
```

If using Gmail, create an App Password for secure access.

---

## Running the System

Run the full pipeline:

```bash
python main.py
```

Pipeline execution:

- Email Monitoring
- Invoice Download
- OCR / Text Extraction
- AI Data Extraction
- Expense Categorization
- Database Storage
- Excel Report Generation

---

## Output

Generated Excel report:

`output/expense_report.xlsx`

**Contents:**

- Invoice list
- Line items
- Category summary
- Spend visualization chart

---

## Demo

A short demonstration video showing the full pipeline working end-to-end is included.

The demo shows:

- Sending an invoice via email
- Running the automation pipeline
- Extracting invoice data
- Storing data in SQLite
- Generating the Excel analytics report

### Demo Video

**Link:** https://drive.google.com/file/d/17VdAK931y-KQMvB1YNb3H0Zb75UzUhqe/view?usp=share_link


## Known Limitations

- Table extraction accuracy varies with invoice layouts.
- OCR accuracy decreases with low-quality scans.
- Vendor categorization rules may need expansion for new vendors.

---

## Improvements With More Time

If extended further, the system could include:

- Web dashboard for expense analytics
- Vendor classification learning system
- Automated email delivery of reports
- Cloud storage integration
- Support for multi-currency invoices
- Better line-item table extraction using document layout models

---

## Author

Mukul Kumar

GitHub: https://github.com/Mukul2425

LinkedIn: https://www.linkedin.com/in/mukul-kumar-090a0b25a/
