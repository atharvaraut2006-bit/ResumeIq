import os
from werkzeug.datastructures import FileStorage

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_level1(file: FileStorage, max_size: int) -> tuple[bool, str, str]:
    """
    Level 1 File Validation:
    Checks existence, extension, non-empty size, MIME magic bytes, and uncorrupted file headers.
    Returns: (is_valid, error_code, user_message)
    """
    if not file or file.filename == '':
        return False, "NO_FILE", "Please select a file to upload."
        
    filename = file.filename
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if ext not in ALLOWED_EXTENSIONS:
        return False, "UNSUPPORTED_FORMAT", f"Invalid file format '.{ext}'. Supported formats: PDF, DOCX."
        
    # Check file size & non-empty
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size == 0:
        return False, "EMPTY_FILE", "This file appears to be empty or contains 0 bytes. Please upload a valid resume."
        
    if file_size > max_size:
        max_mb = max_size // (1024 * 1024)
        return False, "FILE_TOO_LARGE", f"File size exceeds maximum allowed limit of {max_mb}MB."
        
    # Magic bytes check to prevent malicious executables renamed as .pdf/.docx
    header = file.read(8)
    file.seek(0)
    
    if ext == 'pdf' and not header.startswith(b'%PDF'):
        return False, "CORRUPTED_FILE", "We couldn't read this file. The PDF header appears corrupted or invalid."
    elif ext == 'docx' and not header.startswith(b'PK\x03\x04'):
        return False, "CORRUPTED_FILE", "We couldn't read this file. The DOCX file appears corrupted or invalid."
        
    return True, "VALID_FILE", ""
