# app/matching/config.py

MATCHING_CONFIG = {
    "weights": {
        "technical_skills": 0.30,
        "soft_skills": 0.10,
        "experience": 0.15,
        "responsibilities": 0.15,
        "projects": 0.10,
        "education": 0.10,
        "preferred_skills": 0.05,
        "certifications": 0.05
    },
    "semantic_thresholds": {
        "strong_match": 0.85,
        "related_match": 0.70
    },
    "score_categories": [
        {"min": 90, "label": "Excellent Match"},
        {"min": 80, "label": "Strong Match"},
        {"min": 70, "label": "Good Match"},
        {"min": 60, "label": "Moderate Match"},
        {"min": 40, "label": "Weak Match"},
        {"min": 0, "label": "Low Match"}
    ]
}

def get_score_category(score: float) -> str:
    for cat in MATCHING_CONFIG["score_categories"]:
        if score >= cat["min"]:
            return cat["label"]
    return "Low Match"
