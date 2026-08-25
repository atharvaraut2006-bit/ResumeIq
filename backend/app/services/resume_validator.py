import re
from flask import current_app

# Only strict explicit non-resume document patterns
NON_RESUME_NEGATIVE_PATTERNS = [
    r'\bexam\s+question\s+paper\b',
    r'\bclass\s+timetable\b',
    r'\bsemester\s+grade\s+card\b',
    r'\bcourse\s+syllabus\s+20\d\d\b'
]

SECTION_KEYWORDS = {
    'contact': [
        r'[\w\.-]+@[\w\.-]+\.\w+',
        r'\+?\d[\d\s-]{8,}\d',
        r'linkedin\.com',
        r'github\.com',
        r'\bphone\b',
        r'\bemail\b'
    ],
    'education': [
        r'\beducation\b', r'\bdegree\b', r'\buniversity\b', r'\bcollege\b',
        r'\bb\.tech\b', r'\bbtech\b', r'\bb\.e\b', r'\bcomputer science\b',
        r'\bbachelor\b', r'\bmaster\b', r'\bcgpa\b', r'\bgpa\b', r'\bhsc\b', r'\bssc\b'
    ],
    'skills': [
        r'\bskills\b', r'\btechnical skills\b', r'\bprogramming\b', r'\btechnologies\b',
        r'\btools\b', r'\bproficiencies\b', r'\bc\+\+\b', r'\bpython\b', r'\bjava\b', r'\bhtml\b'
    ],
    'experience': [
        r'\bexperience\b', r'\bwork history\b', r'\bemployment\b', r'\binternship\b',
        r'\bdeveloper\b', r'\bengineer\b', r'\banalyst\b', r'\bwork experience\b'
    ],
    'projects': [
        r'\bprojects\b', r'\bpersonal projects\b', r'\bacademic projects\b', r'\bkey projects\b', r'\bproject\b'
    ]
}

def validate_resume_content_level2(raw_text: str) -> dict:
    """
    Level 2 Resume Content Classification:
    Evaluates multi-signal structure (Contact, Education, Skills, Experience, Projects)
    and checks for negative non-resume patterns.
    """
    if not raw_text or len(raw_text.strip()) < 20:
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
            
    # Contact Info Bonus
    if signals.get('contact'):
        signal_score += 0.15
        
    confidence = min(0.98, max(0.05, round(signal_score, 2)))
    threshold = current_app.config.get('RESUME_VALIDATION_THRESHOLD', 0.35)
    
    # Resilient check: ANY 2 signals detected or presence of skills/education is VALID!
    total_signals_detected = sum(1 for v in signals.values() if v)
    is_resume = (confidence >= threshold) or (total_signals_detected >= 2) or signals.get('skills') or signals.get('education')
    
    if is_resume:
        return {
            "is_resume": True,
            "confidence": max(confidence, 0.85),
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
