import os
import mimetypes
import fitz  # PyMuPDF
import docx
import easyocr
import re
import pandas as pd
import google.generativeai as genai

# --- Gemini API Setup ---
genai.configure(api_key="AIzaSyBk_P8f6O-EMVc6YJKBnyNn1LW0jTLXeEY")
model = genai.GenerativeModel("gemini-1.5-flash")

# --- OCR reader ---
reader = easyocr.Reader(['en'])

def extract_text_from_file(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)

    if mime_type:
        if mime_type.startswith("image/"):
            return extract_from_image(file_path)
        elif mime_type == "application/pdf":
            return extract_from_pdf(file_path)
        elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return extract_from_docx(file_path)
        elif mime_type == "text/plain":
            return extract_from_txt(file_path)
        elif mime_type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            return extract_from_excel(file_path)

    raise ValueError(f"Unsupported or unknown file type: {file_path}")

# --- File-specific extraction functions ---
def extract_from_image(file_path):
    results = reader.readtext(file_path, detail=0)
    return "\n".join(results)

def extract_from_pdf(file_path):
    text = ""
    pdf = fitz.open(file_path)
    for page in pdf:
        text += page.get_text()
    return text.strip()

def extract_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_from_txt(file_path):
    with open(file_path, 'r', encoding="utf-8") as f:
        return f.read()

def extract_from_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        return df.to_string(index=False)
    except Exception as e:
        return f"Could not read Excel file: {e}"

# --- Content validation ---
def validate_content(text):
    patterns = [
        r"\bdiagnosis\b", r"\bsymptom\b", r"\btreatment\b", r"\bICD\b",
        r"\bmedication\b", r"\bdosage\b", r"\bprescription\b",
        r"\btake\s+\d+", r"\brefills?\b"
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)

# --- Gemini analysis ---
def generate_analysis(text):
    if not validate_content(text):
        return "Please provide valid medical prescription or diagnostic content."

    prompt = f"""
You are a medical coding assistant. Analyze the following medical content and generate a full structured report with:


1. Patient Demographics (if any)
2. Diagnosis and ICD-10 codes
3. Symptoms mentioned
4. Treatment Plan
5. Medications and Dosage
6. Medical Coding Summary
7. Medical Codes (list all relevant ICD-10, CPT, or other codes separately)

Important instructions:
- Do not provide hypothetical codes or suggestions for missing information.
- If the desease or treatment is not clear, please provide a list of possible codes.

Text:
{text}
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error during Gemini API call: {e}"

# --- Main process ---
def process_medical_file(file_path):
    try:
        text = extract_text_from_file(file_path)
        print("Extracted Text:\n", text)
        report = generate_analysis(text)
        print("\nAnalysis Report:\n", report)
    except Exception as e:
        print("Error:", e)

# --- Example ---
if __name__ == "__main__":
    file_path = "ColorRx-English-Logo-HTWT-Generics.docx"  # Change this to your actual file
    process_medical_file(file_path)