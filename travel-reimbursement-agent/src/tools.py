from datetime import datetime
from .models import ClaimModel

def check_receipts(claim: ClaimModel) -> dict:
    """
    Any item > $25 requires receipt.
    Airfare always requires receipt.
    Lodging always requires receipt.
    Returns {"missing_receipts": list_of_items, "manual_review_required": bool}
    """
    missing = []
    for item in claim.items:
        requires_receipt = False
        if item.amount > 25:
            requires_receipt = True
        if item.category.lower() in ["airfare", "lodging"]:
            requires_receipt = True
        
        if requires_receipt and not item.receipt_attached:
            missing.append(item.model_dump())
            
    return {
        "missing_receipts": missing,
        "manual_review_required": len(missing) > 0
    }

def check_limits(claim: ClaimModel) -> dict:
    """
    Meals: $75/day
    Lodging: $200/night
    Ground transport: $50/day
    """
    # Assuming trip days is (trip_end - trip_start) + 1 if same day, just simple parsing
    try:
        start = datetime.strptime(claim.trip_start, "%Y-%m-%d")
        end = datetime.strptime(claim.trip_end, "%Y-%m-%d")
        days = max(1, (end - start).days + 1)
        nights = max(1, (end - start).days)
    except ValueError:
        days = 1
        nights = 1

    ineligible_categories = [
        "alcohol", "minibar", "spa", "gym", "personal entertainment", 
        "in-room movies", "personal shopping", "gifts", "traffic fines", 
        "penalties", "late fees", "personal/non-business expense"
    ]

    total_claimed = 0.0
    total_allowed = 0.0

    limit_details = []

    # Calculate limits by summing categories
    # In a more advanced version, we might sum per day, but here we compare total category claim to total category limit across the trip.
    cat_totals = {}
    for item in claim.items:
        c = item.category.lower()
        cat_totals[c] = cat_totals.get(c, 0.0) + item.amount

    for item in claim.items:
        c = item.category.lower()
        claimed = item.amount
        total_claimed += claimed

        # Ineligible
        if c in ineligible_categories:
            allowed = 0.0
        # Meals
        elif c == "meals":
            allowed = min(claimed, 75.0 * days)
            # if we have multiple meal items, they share the max. For simplicity we just do min over the sum.
            # But we evaluate item by item in this simple engine, so:
            # Let's adjust to evaluate per category overall if needed, or just apply proportional logic.
            # Actually, doing it category wide is better:
            pass
        else:
            allowed = claimed # defaults to full if no specific limit
            
    # Let's do category-wide limit enforcement instead of per-item
    total_allowed_calculated = 0.0
    for cat, amount in cat_totals.items():
        allowed = amount
        if cat in ineligible_categories:
            allowed = 0.0
        elif cat == "meals":
            allowed = min(amount, 75.0 * days)
        elif cat == "lodging":
            allowed = min(amount, 200.0 * nights)
        elif cat == "ground_transport":
            allowed = min(amount, 50.0 * days)
        
        limit_details.append({
            "category": cat,
            "claimed": amount,
            "allowed": allowed,
            "deducted": amount - allowed
        })
        total_allowed_calculated += allowed

    return {
        "claimed": sum(cat_totals.values()),
        "allowed": total_allowed_calculated,
        "deducted": sum(cat_totals.values()) - total_allowed_calculated,
        "details": limit_details
    }

def check_airfare_class(claim: ClaimModel) -> dict:
    """
    Economy: eligible
    Business/first: MANUAL_REVIEW
    """
    manual_review = False
    for item in claim.items:
        if item.category.lower() == "airfare":
            desc = item.description.lower()
            if "business" in desc or "first" in desc:
                manual_review = True
    return {
        "manual_review_required": manual_review
    }

def check_timeliness(claim: ClaimModel) -> dict:
    """
    Submitted within 30 days of trip end.
    """
    try:
        end = datetime.strptime(claim.trip_end, "%Y-%m-%d")
        sub = datetime.strptime(claim.submitted_date, "%Y-%m-%d")
        diff = (sub - end).days
        manual_review = diff > 30
    except ValueError:
        manual_review = True # Invalid date -> manual review

    return {
        "manual_review_required": manual_review,
        "days_to_submit": diff if 'diff' in locals() else None
    }

def check_approval_threshold(amount: float) -> dict:
    """
    <= 500: AUTO_APPROVE
    > 500 and <= 2000: MANAGER_TIER (treated as APPROVE for final output if no other issues)
    > 2000: MANUAL_REVIEW
    """
    manual_review = amount > 2000
    tier = "AUTO_APPROVE"
    if 500 < amount <= 2000:
        tier = "MANAGER_TIER"
    elif amount > 2000:
        tier = "MANUAL_REVIEW"
        
    return {
        "manual_review_required": manual_review,
        "tier": tier
    }

def extract_receipt_data(file_path: str) -> dict:
    """
    Extracts text from PDF or Image using open-source Python libraries.
    - PDF: Uses `pypdf`
    - Images: Uses `pytesseract` (Requires Tesseract-OCR installed on the OS)
    """
    import os
    import re
    ext = os.path.splitext(file_path)[1].lower()
    extracted_text = ""
    
    if ext == '.pdf':
        try:
            import pypdf
            with open(file_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    extracted_text += page.extract_text() + "\n"
        except ImportError:
            extracted_text = "ERROR: pypdf not installed. Run: pip install pypdf"
        except Exception as e:
            extracted_text = f"ERROR: Failed to extract PDF. {str(e)}"
            
    elif ext in ['.png', '.jpg', '.jpeg']:
        try:
            import pytesseract
            from PIL import Image
            extracted_text = pytesseract.image_to_string(Image.open(file_path))
        except ImportError:
            extracted_text = "ERROR: pytesseract/pillow not installed. Run: pip install pytesseract pillow"
        except Exception as e:
            extracted_text = f"ERROR: OCR Failed. Please ensure Tesseract-OCR is installed on your Windows machine. {str(e)}"
    else:
        return {"error": "Unsupported file format. Please upload PDF, PNG, or JPG."}
        
    if "ERROR:" in extracted_text:
        return {
            "extracted_amount": 0.0,
            "extracted_date": "Unknown",
            "merchant": "Unknown",
            "category": "Unknown",
            "raw_text": extracted_text.strip()[:1000],
            "file_type": ext
        }

    try:
        from .groq_client import GroqLLMProvider
        import json
        llm = GroqLLMProvider()
        system_prompt = "You are a data extraction assistant. Extract receipt details from the provided OCR text. Return a JSON object with keys: 'amount' (float), 'date' (YYYY-MM-DD string), 'merchant' (string), and 'category' (string, choose from: Flight, Lodging, Meals, Conference, Other). Output ONLY valid JSON, without any markdown formatting or <think> tags."
        prompt = f"Extract details from this OCR text:\n\n{extracted_text.strip()[:2000]}"
        response_text = llm.invoke(prompt, system_prompt=system_prompt)
        
        # Strip potential <think> blocks that might confuse regex
        response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL).strip()
        
        # Clean response to get just the JSON block
        # Try to find a JSON code block first
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(1))
        else:
            # Fallback to finding the first { ... } that parses successfully
            import ast
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx+1]
                data = json.loads(json_str)
            else:
                data = {}
            
        return {
            "extracted_amount": float(data.get("amount", 0.0)),
            "extracted_date": data.get("date", "Unknown"),
            "merchant": data.get("merchant", "Unknown"),
            "category": data.get("category", "Meals"),
            "raw_text": extracted_text.strip()[:1000],
            "file_type": ext
        }
    except Exception as e:
        print("LLM Extraction failed, falling back to regex. Error:", e)
        # Fallback to regex
        amounts = re.findall(r'\$?(\d+\.\d{2})', extracted_text)
        guessed_amount = float(amounts[0]) if amounts else 0.0
            
        return {
            "extracted_amount": guessed_amount,
            "extracted_date": "Unknown",
            "merchant": "Unknown",
            "category": "Unknown",
            "raw_text": extracted_text.strip()[:1000],
            "file_type": ext
        }

