from app.services.resume_parser import extract_sections, extract_contact_info

def test_extract_sections():
    text = """
    JOHN DOE
    
    SUMMARY
    Experienced software engineer.
    
    EDUCATION
    B.Tech Computer Science
    
    EXPERIENCE
    Software Engineer at Google
    """
    sections = extract_sections(text)
    
    assert "summary" in sections
    assert "Experienced software engineer." in sections["summary"]
    
    assert "education" in sections
    assert "B.Tech Computer Science" in sections["education"]
    
    assert "experience" in sections
    assert "Software Engineer at Google" in sections["experience"]

def test_extract_contact_info():
    text = """
    John Doe
    john.doe@example.com
    +91 98765 43210
    https://linkedin.com/in/johndoe
    https://github.com/johndoe
    """
    
    contact = extract_contact_info(text, text)
    
    assert contact["name"] == "John Doe"
    assert contact["email"] == "john.doe@example.com"
    assert contact["phone"] == "+91 98765 43210"
    assert contact["linkedin"] == "https://linkedin.com/in/johndoe"
    assert contact["github"] == "https://github.com/johndoe"
