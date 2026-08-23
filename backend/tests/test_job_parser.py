from app.services.job_section_detector import detect_job_sections
from app.services.job_requirement_extractor import extract_experience_requirements

def test_job_section_detector():
    text = """
    About the Role
    We are looking for a software engineer.
    
    Requirements
    - Python
    - SQL
    
    Nice to have
    - AWS
    - Docker
    """
    sections = detect_job_sections(text)
    
    assert "description" in sections
    assert "required_requirements" in sections
    assert "preferred_requirements" in sections
    assert "Python" in sections["required_requirements"]
    assert "Docker" in sections["preferred_requirements"]

def test_extract_experience():
    text = "We want someone with 3-5 years of experience in tech."
    exp = extract_experience_requirements(text)
    
    assert len(exp) == 1
    assert exp[0]["minimum_years"] == 3
    assert exp[0]["maximum_years"] == 5
    
    text2 = "At least 2+ years of experience required."
    exp2 = extract_experience_requirements(text2)
    assert exp2[0]["minimum_years"] == 2
    assert exp2[0]["maximum_years"] is None
