import json
import re
from app.models.resume import Resume
from app.models.job_match import JobMatch, SkillMatch

WEAK_VERBS = ['worked', 'did', 'helped', 'made', 'responsible for', 'handled', 'was']

STRONG_VERBS = {
    'worked': 'Developed / Engineered / Executed',
    'did': 'Implemented / Achieved',
    'helped': 'Collaborated / Facilitated / Supported',
    'made': 'Designed / Created / Architected',
    'responsible for': 'Managed / Orchestrated / Directed',
    'handled': 'Administered / Resolved / Optimized',
    'was': '[Use an active verb describing the action]'
}

def analyze_and_suggest_rewrites(resume: Resume, job_match: JobMatch, mode: str = 'balanced') -> list[dict]:
    """
    Generates safe, non-fabricating suggestions tailored to conservative, balanced, or aggressive mode.
    """
    suggestions = []
    mode_lower = (mode or 'balanced').lower()
    
    if not resume.parsed_data:
        return suggestions
        
    try:
        parsed = json.loads(resume.parsed_data)
    except Exception:
        return suggestions
        
    # Check experience & project bullets
    for proj_idx, proj in enumerate(parsed.get("projects", [])):
        desc = proj.get("description") or proj.get("raw") or ""
        if not desc: continue
        
        lower_desc = desc.lower()
        for weak in WEAK_VERBS:
            if lower_desc.startswith(weak) or f" {weak} " in lower_desc:
                suggestions.append({
                    "section": "projects",
                    "original_text": desc,
                    "suggested_text": desc.replace(weak, f"[{STRONG_VERBS[weak]}]", 1).replace(weak.capitalize(), f"[{STRONG_VERBS[weak]}]", 1),
                    "reason": f"Uses weak verb '{weak}'. [{mode_lower.upper()} MODE] Replace with strong technical action verbs for higher ATS parser scoring.",
                    "impact": "Medium"
                })
                break
                
        if mode_lower in ['balanced', 'aggressive'] and not re.search(r'\d+%?', desc):
            suggestions.append({
                "section": "projects",
                "original_text": desc,
                "suggested_text": f"{desc} [Add measurable outcome/metric here, e.g., 'improving latency by 25%' or 'handling 100+ requests']",
                "reason": f"[{mode_lower.upper()} MODE] Measurable metrics significantly boost ATS keyword & impact scores.",
                "impact": "High"
            })
            
    # Check summary & missing skills
    skill_matches = SkillMatch.query.filter_by(job_match_id=job_match.id).all()
    missing_required = [sm.skill_name for sm in skill_matches if sm.match_type == "missing" and sm.required]
    
    if missing_required:
        missing_str = ", ".join(missing_required[:(5 if mode_lower == 'aggressive' else 3)])
        summary = parsed.get("summary", "") or "Aspiring Data Science & Software Engineer."
        
        if mode_lower == 'aggressive':
            suggestions.append({
                "section": "skills",
                "original_text": "Missing critical JD skills",
                "suggested_text": f"Skills: Include target skills ({missing_str}) in your Technical Skills section if verified.",
                "reason": "[AGGRESSIVE MODE] Maximize keyword density by adding verified required skills to your Skills list.",
                "impact": "High"
            })
        elif mode_lower == 'balanced':
            suggestions.append({
                "section": "summary",
                "original_text": summary,
                "suggested_text": f"{summary} [If experienced with {missing_str}, explicitly mention them in your summary.]",
                "reason": "[BALANCED MODE] Cross-reference missing JD keywords in summary.",
                "impact": "High"
            })

    return suggestions
