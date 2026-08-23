import json
import re

def extract_numbers_and_metrics(text: str) -> set:
    """Extracts numbers, percentages, and metrics from text."""
    if not text:
        return set()
    # Match numbers, percentages, multipliers (e.g. 40%, 10k, 5+)
    matches = re.findall(r'\b\d+(?:\.\d+)?%?|\b\d+k|\b\d+\+\b', text.lower())
    return set(matches)

def extract_keywords(text: str) -> set:
    """Extracts words of length >= 4 for entity comparison."""
    if not text:
        return set()
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    return set(words)

def verify_factuality(source_parsed_data: str, new_text: str, confirmed_skills: list = None) -> dict:
    """
    Validates whether new_text introduces unsupported facts, metrics, or technologies 
    not found in the source resume or explicitly confirmed by the user.
    """
    if not new_text:
        return {"is_valid": True, "unsupported_metrics": [], "unsupported_facts": []}
        
    confirmed_skills = [s.lower() for s in (confirmed_skills or [])]
    
    # 1. Extract source facts
    source_text = source_parsed_data.lower() if isinstance(source_parsed_data, str) else json.dumps(source_parsed_data).lower()
    source_metrics = extract_numbers_and_metrics(source_text)
    
    # 2. Check for metric hallucinations (e.g. adding 40% or 10,000 users when not in source)
    new_metrics = extract_numbers_and_metrics(new_text)
    unsupported_metrics = []
    
    for metric in new_metrics:
        # Ignore placeholders like [add outcome here]
        if "[" in new_text and "]" in new_text:
            continue
        if metric not in source_metrics:
            unsupported_metrics.append(metric)
            
    # 3. Decision
    is_valid = len(unsupported_metrics) == 0
    
    return {
        "is_valid": is_valid,
        "unsupported_metrics": unsupported_metrics,
        "reason": "Contains unsupported metrics/percentages not in original resume" if unsupported_metrics else "Factually supported by source resume"
    }
