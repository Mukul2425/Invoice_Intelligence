import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def empty_invoice_schema():

    return {
        "vendor_name": "",
        "invoice_number": "",
        "invoice_date": "",
        "due_date": "",
        "total_amount": "",
        "tax": "",
        "payment_status": "",
        "line_items": []
    }

def build_prompt(invoice_text):

    prompt = f"""
You are an AI system that extracts structured data from invoices.

Return ONLY valid JSON. Do NOT include explanations, text, or markdown.

JSON structure must be exactly:

{{
  "vendor_name": "",
  "invoice_number": "",
  "invoice_date": "",
  "due_date": "",
  "total_amount": "",
  "tax": "",
  "payment_status": "",
  "line_items": [
    {{
      "description": "",
      "quantity": "",
      "unit_price": "",
      "item_total": ""
    }}
  ]
}}

Rules:
- Return ONLY JSON
- Do not wrap JSON in markdown
- Do not include any text before or after JSON
- Numbers must not include currency symbols
- If a field is missing, leave it empty

Invoice text:
{invoice_text}
"""
    return prompt

def extract_with_llm(invoice_text):

    try:

        prompt = build_prompt(invoice_text)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:

        print("LLM request failed:", e)

        return None

def parse_llm_json(response_text):

    try:

        response_text = response_text.strip()

        # remove markdown blocks
        if "```" in response_text:
            parts = response_text.split("```")
            response_text = parts[1]

        # find JSON start
        start = response_text.find("{")
        end = response_text.rfind("}")

        if start != -1 and end != -1:
            response_text = response_text[start:end+1]

        data = json.loads(response_text)

        return data

    except Exception as e:

        print("LLM JSON parsing failed:", e)
        return None
    
def validate_invoice(data):

    if not data:
        return False

    if not data.get("total_amount"):
        return False

    if not data.get("vendor_name"):
        return False

    return True
def normalize_values(data):

    if data.get("total_amount"):
        data["total_amount"] = str(data["total_amount"]).replace("$", "").strip()

    if data.get("tax"):
        data["tax"] = str(data["tax"]).replace("$", "").strip()

    return data

def extract_invoice_data(invoice_text):

    llm_output = extract_with_llm(invoice_text)

    if not llm_output:
        print("LLM failed — using fallback parser")
        from ai_extraction.fallback_parser import regex_fallback
        return regex_fallback(invoice_text)

    parsed = parse_llm_json(llm_output)

    if validate_invoice(parsed):

        print("LLM extraction successful")

        parsed = normalize_values(parsed)

        return parsed

    else:

        print("LLM extraction incomplete — fallback needed")

        from ai_extraction.fallback_parser import regex_fallback
        return regex_fallback(invoice_text)
    
if __name__ == "__main__":

    from document_processing.document_reader import read_document
    from database.store import save_invoice

    sample_file = "bills/2026-03/wordpress-pdf-invoice-plugin-sample.pdf"

    text = read_document(sample_file)

    data = extract_invoice_data(text)

    print(json.dumps(data, indent=2))

    save_invoice(data, sample_file)