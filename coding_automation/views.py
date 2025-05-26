from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from medical_processor.transcript import process_medical_file
import os
import re
import tempfile

@csrf_exempt  # For simplicity, in production use proper CSRF handling
def process_medical_document(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)
    
    uploaded_file = request.FILES['file']
    
    try:
        # Create a temporary file to process
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name
        
        # Process the file
        extracted_text = extract_text_from_file(tmp_file_path)
        full_report = generate_analysis(extracted_text)
        
        # Parse the analysis report into sections
        analysis_sections = parse_report_sections(full_report)
        
        # Clean up
        os.unlink(tmp_file_path)
        
        response_data = {
            'status': 'success',
            'extracted_text': extracted_text,
            'analysis_report': {
                'full_report': full_report,
                'sections': analysis_sections
            }
        }
        
        return JsonResponse(response_data)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    

def parse_report_sections(full_report):
    """Parse the numbered sections from the analysis report"""
    # print("=== Full Report ===")  # Debug
    # print(full_report)
    # print("==================")
    sections = {}
    current_section = None
    current_content = []
    
   # Split the report into lines
    lines = full_report.split('\n')
    
    for line in lines:
        # More flexible section header detection
        section_match = re.match(r'^\s*\*?\*?(\d+)\.\s+(.*?)\*?\*?\s*:?\s*$', line.strip())
        if section_match:
            if current_section:
                # Save the previous section
                sections[current_section] = '\n'.join(current_content).strip()
            
            # Start new section
            section_num = section_match.group(1)
            section_name = section_match.group(2).lower().replace(' ', '_').replace('-', '_')
            current_section = f"{section_num}_{section_name}"
            current_content = []
        elif current_section:
            # Skip empty lines between sections
            if not line.strip() and not current_content:
                continue
            current_content.append(line.rstrip())
    
    # Add the last section
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    # # Debug output
    # print("=== Final Parsed Sections ===")
    # for section, content in sections.items():
    #     print(f"\nSection {section}:")
    #     print(content)
    
    return sections


# Alternatively, you can use the process_medical_file function directly if you prefer
def extract_text_from_file(file_path):
    from medical_processor.transcript import extract_text_from_file as _extract
    return _extract(file_path)

def generate_analysis(text):
    from medical_processor.transcript import generate_analysis as _analyze
    return _analyze(text)