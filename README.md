# Invoice Intelligence

Automated invoice ingestion and analytics pipeline that reads attachments from email, extracts structured finance data with OCR + AI, stores records in SQLite, and generates a business-ready Excel report.

## Why This Project Matters

Finance teams lose time manually collecting invoice details from mixed formats like scanned PDFs, image receipts, and digital invoices.

This project turns that manual workflow into an automated pipeline:

Email Inbox -> Attachment Download -> OCR/Text Extraction -> AI + Regex Parsing -> Categorization -> Database Storage -> Excel Report

## Highlights

- Automated email monitoring for invoice attachments
- OCR support for image-based and scanned invoices
- AI extraction using Gemini with regex fallback
- Rule-based + AI vendor categorization
- Duplicate protection and incremental file processing
- Structured logging, retry, timeout, and backoff support
- Excel summary report with category-level spend visualization
- Unit tests and CI checks on push and pull request

## Architecture

```mermaid
flowchart LR
	A[Email Inbox] --> B[email_monitor]
	B --> C[bills/YYYY-MM attachments]
	C --> D[document_processing]
	D --> E[ai_extraction]
	E --> F[categorization]
	F --> G[database]
	G --> H[reports/excel_report]
	H --> I[output/expense_report_YYYY_MM.xlsx]
```

## Project Structure

```text
Invoice_Intelligence/
|- main.py
|- requirements.txt
|- .env.example
|- README.md
|- Project_Readme.md
|- config/
|  |- settings.py
|  |- logging_config.py
|- email_monitor/
|  |- email_reader.py
|- document_processing/
|  |- document_reader.py
|- ai_extraction/
|  |- extractor.py
|  |- fallback_parser.py
|- categorization/
|  |- categorize.py
|- database/
|  |- db.py
|  |- models.py
|  |- store.py
|  |- processing_state.py
|- reports/
|  |- excel_report.py
|- tests/
|  |- test_categorization.py
|  |- test_fallback_parser.py
|  |- test_processing_state.py
|  |- test_store.py
|- logs/
|- bills/
|- output/
|- .github/workflows/python-ci.yml
```

## Quick Start

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install OCR System Dependencies (macOS)

```bash
brew install tesseract poppler
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit .env with:

```env
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
GEMINI_API_KEY=your_gemini_api_key

# Optional resilience tuning
IMAP_TIMEOUT_SECONDS=20
IMAP_RETRY_ATTEMPTS=3
LLM_TIMEOUT_SECONDS=30
LLM_RETRY_ATTEMPTS=3
```

### 4. Run the Pipeline

```bash
python main.py
```

## Output

Generated report path:

```text
output/expense_report_YYYY_MM.xlsx
```

Report contains:

- Invoices sheet
- Line Items sheet
- Category Summary sheet with chart

## Reliability Features

- Centralized startup config validation
- Retry with exponential backoff for IMAP and Gemini calls
- Timeout controls via environment variables
- Structured, stage-based logging
- Duplicate protection in storage layer
- Incremental processing using file fingerprint (mtime + size)

## Testing

Run unit tests:

```bash
python -m unittest discover -s tests -v
```

Run lint checks:

```bash
ruff check .
```

## CI

GitHub Actions workflow runs automatically on push and pull request:

- Lint job (Ruff)
- Test job (Python 3.11 and 3.12)

Workflow file:

```text
.github/workflows/python-ci.yml
```

## Known Limitations

- OCR quality depends on invoice image quality
- Layout-heavy invoice tables may need stronger parser heuristics
- Vendor category accuracy improves with richer keyword rules

## Roadmap

- Dashboard view for expense analytics
- Smarter vendor learning and category adaptation
- Optional email summary delivery
- Cloud object storage integration

## Author

Mukul Kumar

