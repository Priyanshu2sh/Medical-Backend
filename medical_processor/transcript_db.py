import os
import fitz  # PyMuPDF for PDF
import docx
import easyocr
import re
import json
import mysql.connector
import google.generativeai as genai

# --- Gemini API Setup ---
genai.configure(api_key="AIzaSyBk_P8f6O-EMVc6YJKBnyNn1LW0jTLXeEY")
model = genai.GenerativeModel("gemini-1.5-flash")

# --- Initialize OCR reader ---
reader = easyocr.Reader(['en'])

# --- Connect to MySQL database ---
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # change if using a different user
        password="21july2002@#&",
        database="transcription"
    )

# --- Extract text from files (image/pdf/docx) ---
def extract_text_from_file(file_path):
    if file_path.endswith((".jpg", ".jpeg", ".png", ".webp")):
        results = reader.readtext(file_path, detail=0)
        return "\n".join(results)

    elif file_path.endswith(".pdf"):
        text = ""
        pdf = fitz.open(file_path)
        for page in pdf:
            text += page.get_text()
        return text.strip()

    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    else:
        raise ValueError("Unsupported file type.")

# --- Validate if content contains medical terms ---
def validate_content(text):
    patterns = [
        r"\bdiagnosis\b", r"\bsymptom\b", r"\btreatment\b", r"\bICD\b",
        r"\bmedication\b", r"\bdosage\b", r"\bprescription\b",
        r"\btake\s+\d+", r"\brefills?\b"
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)

# --- Call Gemini API for structured medical analysis ---
def generate_analysis(json_data):
    if not json_data or not validate_content(json_data):
        return "Please provide valid medical prescription or diagnostic content."

    prompt = f"""
You are a medical coding assistant. Analyze the following medical content and generate a full structured report with:
(If given text has multiple patients, please provide a separate report for each patient.)
The text contains medical information. Please extract and summarize the following details:

1. Patient Demographics (if any)
2. Diagnosis and ICD-10 codes
3. Symptoms mentioned
4. Treatment Plan
5. Medications and Dosage
6. Medical Coding Summary
7. Medical Codes (list all relevant ICD-10, CPT, or other codes separately)
(Give all codes by your own, according to desease and treatment)

Important instructions:
- Do not provide hypothetical codes or suggestions for missing information.
- If the desease or treatment is not clear, please provide a list of possible codes.

{json_data}
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error during Gemini API call: {e}"

# --- Fetch data from MySQL and convert to JSON ---
import datetime

def fetch_data_as_json():
    conn = connect_to_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM medical_records")  # your table name
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if not rows:
        raise ValueError("No records found in the database.")

    def convert_dates(obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    return json.dumps(rows, indent=2, default=convert_dates)

# --- Main process using MySQL data ---
def process_data_from_db():
    try:
        json_data = fetch_data_as_json()
        print("Fetched JSON Data:\n", json_data)
        report = generate_analysis(json_data)
        print("\nAnalysis Report:\n", report)
    except Exception as e:
        print("Error:", e)

# --- Main process using file (image/pdf/docx) ---
def process_medical_file(file_path):
    try:
        text = extract_text_from_file(file_path)
        print("Extracted Text:\n", text)
        report = generate_analysis(text)
        print("\nAnalysis Report:\n", report)
    except Exception as e:
        print("Error:", e)

# --- Entry Point ---
if __name__ == "__main__":
    # Use only one of the below depending on your input source

    # Option 1: From MySQL Database
    process_data_from_db()

    # Option 2: From File (uncomment and specify path)
    # file_path = "demo-rx.png"  # replace with your actual file
    # process_medical_file(file_path)