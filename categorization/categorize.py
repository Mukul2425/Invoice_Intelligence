CATEGORY_RULES = {

    "Tools & Software": [
        "amazon web services",
        "aws",
        "google",
        "microsoft",
        "openai",
        "notion",
        "github",
        "slack"
    ],

    "Travel & Petrol": [
        "uber",
        "ola",
        "petrol",
        "fuel",
        "shell"
    ],

    "Utilities": [
        "electric",
        "electricity",
        "water",
        "internet",
        "wifi"
    ],

    "Office Expenses": [
        "office depot",
        "stationery",
        "printing",
        "supplies"
    ]
}

ALLOWED_CATEGORIES = [
    "Office Expenses",
    "Tools & Software",
    "Travel & Petrol",
    "Utilities",
    "Other",
]

NORMALIZED_CATEGORY_LOOKUP = {
    "officeexpenses": "Office Expenses",
    "toolssoftware": "Tools & Software",
    "travelpetrol": "Travel & Petrol",
    "utilities": "Utilities",
    "other": "Other",
}


def _normalize_category(value):
    if not value:
        return "Other"

    lowered = value.lower().replace(" and ", " ").replace("&", " ")
    clean = "".join(ch for ch in lowered if ch.isalpha())
    normalized = NORMALIZED_CATEGORY_LOOKUP.get(clean)

    if normalized:
        return normalized

    return "Other"

def rule_based_category(vendor):

    vendor = vendor.lower()

    for category, keywords in CATEGORY_RULES.items():

        for keyword in keywords:

            if keyword in vendor:
                return category

    return None

from google import genai
from config.settings import get_settings

_client = None


def get_gemini_client():
    global _client

    if _client is None:
        settings = get_settings()
        _client = genai.Client(api_key=settings.gemini_api_key)

    return _client

def llm_category(vendor):

    prompt = f"""
Classify this vendor into one of the categories:

Office Expenses
Tools & Software
Travel & Petrol
Utilities
Other

Vendor:
{vendor}

Return only the category name.
"""

    try:

        response = get_gemini_client().models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text.strip()

    except:
        return "Other"
    

def categorize_invoice(vendor):

    if not vendor:
        return "Other"

    category = rule_based_category(vendor)

    if category:
        return _normalize_category(category)

    llm_result = llm_category(vendor)

    if not llm_result:
        return "Other"
    
    return _normalize_category(llm_result.strip())

if __name__ == "__main__":

    vendor = "Amazon Web Services"

    category = categorize_invoice(vendor)
    