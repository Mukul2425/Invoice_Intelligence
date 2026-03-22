# Finance Automation — Bill & Invoice Intelligence

An end-to-end automation system that reads invoices from email, extracts structured financial data using AI, stores it in a database, and generates expense analytics reports.

---

# Overview

Companies receive invoices from many vendors in different formats.  
This system automatically processes those invoices and produces structured financial insights.

Pipeline:

Email → Invoice Download → OCR/Text Extraction → AI Data Extraction → Categorization → Database Storage → Excel Analytics Report

---

# Features

• Automatic email monitoring for invoice attachments  
• OCR support for scanned invoices and images  
• AI-powered data extraction using Gemini  
• Fallback regex parser for reliability  
• Expense categorization using rules + AI  
• SQLite database storage with relational structure  
• Excel report generation with charts

---

# Tech Stack

Python  
Gemini API  
Tesseract OCR  
PyMuPDF  
SQLite + SQLAlchemy  
OpenPyXL

---

# Project Structure
invoice-intelligence/
│
├── main.py
├── requirements.txt
├── .env.example
│
├── email_monitor/
├── document_processing/
├── ai_extraction/
├── categorization/
├── database/
├── reports/
│
├── bills/
├── output/
└── logs/


---

# Setup Instructions

### 1 Install Dependencies

```bash
pip install -r requirements.txt
```

### 2 Install Tesseract OCR (Mac)

```bash
brew install tesseract
```

### 3 Install Poppler (for pdf2image) (Mac)

```bash
brew install poppler
```

### 4 Configure Environment Variables

Copy the example file:

```bash
cp .env.example .env
```

Edit `.env` and fill in:

```
EMAIL_ADDRESS=
EMAIL_PASSWORD=
GEMINI_API_KEY=
```

Optional resilience settings:

```
IMAP_TIMEOUT_SECONDS=20
IMAP_RETRY_ATTEMPTS=3
LLM_TIMEOUT_SECONDS=30
LLM_RETRY_ATTEMPTS=3
```

#### (Optional) If using Gmail, generate an App Password

1. Ensure 2-Step Verification is enabled for your Google account.
2. Go to https://myaccount.google.com/security.
3. Under "Signing in to Google" click **App passwords**.
4. Select **Mail** as the app and **Other (Custom name)** (e.g., "Invoice Intelligence").
5. Click **Generate**, then copy the 16‑character password.
6. Use that value for `EMAIL_PASSWORD` in `.env`.

### Running the Pipeline

```bash
python main.py
```

### Running Tests

```bash
source venv/bin/activate
python -m unittest discover -s tests -v
```

### CI Automation

GitHub Actions now runs the test suite on every push and pull request using Python 3.11 and 3.12.
It also runs Ruff lint checks.

Workflow file:

- .github/workflows/python-ci.yml

### Linting

```bash
ruff check .
```

This will:

- Check email inbox for invoices
- Download attachments
- Extract invoice data using AI
- Categorize expenses
- Store data in SQLite database
- Generate Excel expense report

Pipeline optimization:

- The pipeline now tracks file fingerprints (mtime + size) and skips unchanged invoice files on later runs.

### Generated Output

Excel report with:

- Sheet 1 — Invoice list
- Sheet 2 — Line items
- Sheet 3 — Category summary + chart

Location:

`output/expense_report.xlsx`

### Example Workflow

Send an email containing a PDF invoice → The system automatically processes it and updates the expense report.

## Initiative Features

Beyond the assignment requirements, the system includes several production-style improvements:

- Hybrid AI extraction pipeline with LLM + regex fallback
- Hybrid expense categorization (rule-based + AI)
- Duplicate invoice detection
- Processing logs for traceability
- Smart pipeline that skips already processed invoices
- Automated Excel analytics report with charts

### Known Limitations

- Table extraction accuracy depends on invoice layout
- OCR accuracy varies for low quality scans
- Vendor categorization may require rule expansion

### Future Improvements

- Web dashboard for expense analytics
- Vendor learning system for better categorization
- Cloud storage integration
- Email report delivery automation

### Author

Mukul Kumar

