import fitz
import re

def extract_text_from_pdf(file_path: str) -> tuple[bool, str]:
    """
    Extracts text from a PDF file using PyMuPDF.
    Returns (success, result_text_or_error_message).
    """
    try:
        doc = fitz.open(file_path)
        
        if doc.page_count == 0:
            return False, "EMPTY_DOCUMENT"
            
        full_text = []
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            full_text.append(text)
            
        doc.close()
        
        combined_text = "\n".join(full_text)
        cleaned_text = clean_extracted_text(combined_text)
        
        # Check if the PDF is basically an image / scanned
        if len(cleaned_text.strip()) < 50: # Threshold for scanned doc
            return False, "TEXT_EXTRACTION_FAILED"
            
        return True, cleaned_text
        
    except fitz.FileDataError:
        return False, "INVALID_PDF"
    except Exception as e:
        return False, f"INTERNAL_ERROR: {str(e)}"

def clean_extracted_text(text: str) -> str:
    """
    Cleans extracted text without destroying section boundaries.
    """
    # Replace multiple spaces with a single space, but keep newlines
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Replace excessive newlines (more than 2) with just 2 newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()
