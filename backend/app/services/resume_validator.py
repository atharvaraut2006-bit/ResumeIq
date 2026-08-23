import re
from flask import current_app

NON_RESUME_NEGATIVE_PATTERNS = [
    r'\bassignment\b', r'\blab report\b', r'\bhomework\b', r'\bproblem set\b',
    r'\bquestion\s+\d+\b', r'\breferences\b.*\bdoi:\b', r'\bieee\b', r'\babstract\b.*\bintroduction\b',
    r'\btimetable\b', r'\bclass schedule\b', r'\bmarksheet\b', r'\bgrade card\b',
    r'\bcertificate of completion\b', r'\bthis is to certify that\b', r'\bcourse syllabus\b'
]

SECTION_KEYWORDS = {
    'contact': [r'[\w\.-]+@[\w\.-]+\.\w+', r'\+?\d[\d\s-]{8,}\d', r'linkedin\.com', r'github\.com'],
    'education': [r'\beducation\b', r'\bdegree\b', r'\buniversity\b', r'\bcollege\b', r'\bb\.tech\b', r'\bb\.s\b', r'\bbachelor\b', r'\bmaster\b'],
    'skills': [r'\bskills\b', r'\btechnical skills\b', r'\bprogramming\b', r'\btechnologies\b', r'\btools\b', r'\bproficiencies\b'],
    'experience': [r'\bexperience\b', r'\bwork history\b', r'\bemployment\b', r'\binternship\b', r'\bprofessional experience\b'],
    'projects': [r'\bprojects\b', r'\bpersonal projects\b', r'\bacademic projects\b', r'\bkey projects\b']
}

def validate_resume_content_level2(raw_text: str) -> dict:
    """
    Level 2 Resume Content Classification:
    Evaluates multi-signal structure (Contact, Education, Skills, Experience, Projects)
    and checks for negative non-resume patterns (assignments, papers, marksheets, timetables).
    """
    if not raw_text or len(raw_text.strip()) < 50:
        return {
            "is_resume": False,
            "confidence": 0.0,
            "document_type": "empty",
            "status": "EMPTY_FILE",
            "reason": "This document contains insufficient text to be analyzed as a resume.",
            "detected_signals": {}
        }
        
    lower_text = raw_text.lower()
    
    # 1. Check Negative Non-Resume Signals
    negative_hits = 0
    for pattern in NON_RESUME_NEGATIVE_PATTERNS:
        if re.search(pattern, lower_text):
            negative_hits += 1
            
    if negative_hits >= 2:
        return {
            "is_resume": False,
            "confidence": 0.15,
            "document_type": "non_resume",
            "status": "NOT_A_RESUME",
            "reason": "Please check your uploaded file. We couldn't identify this document as a resume. Please upload a valid resume and try again.",
            "detected_signals": {}
        }
        
    # 2. Check Positive Multi-Signal Structures
    signals = {}
    signal_score = 0.0
    
    for category, patterns in SECTION_KEYWORDS.items():
        found = any(re.search(p, lower_text) for p in patterns)
        signals[category] = found
        if found:
            signal_score += 0.20
            
    # Contact Info Bonus (Email/Phone is strong evidence of a person's resume)
    if signals.get('contact'):
        signal_score += 0.15
        
    # Penalty if negative hits exist
    if negative_hits == 1:
        signal_score -= 0.25
        
    confidence = min(0.98, max(0.05, round(signal_score, 2)))
    threshold = current_app.config.get('RESUME_VALIDATION_THRESHOLD', 0.70)
    
    # Fresher resilience check: Education + Skills + Projects (even without experience) is VALID!
    fresher_valid = signals.get('education') and signals.get('skills') and (signals.get('projects') or signals.get('contact'))
    
    is_resume = (confidence >= threshold) or fresher_valid
    
    if is_resume:
        return {
            "is_resume": True,
            "confidence": max(confidence, 0.75),
            "document_type": "resume",
            "status": "VALID",
            "reason": "Resume content and structure verified successfully.",
            "detected_signals": signals
        }
    else:
        return {
            "is_resume": False,
            "confidence": confidence,
            "document_type": "non_resume",
            "status": "NOT_A_RESUME",
            "reason": "Please check your uploaded file. We couldn't identify this document as a resume. Please upload a valid resume and try again.",
            "detected_signals": signals
        }
