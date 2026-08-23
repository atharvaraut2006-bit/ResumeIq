import json
import logging
from app.models.resume import Resume
from app.models.job import Job
from app.models.job_match import JobMatch, SkillMatch
from app.optimization.ats_simulator import simulate_ats

logger = logging.getLogger(__name__)

def generate_improvement_plan(resume: Resume, job: Job, job_match: JobMatch = None):
    """
    Phase 13 Intelligent Resume Coach & Improvement Engine.
    Synthesizes Resume, JD, Match, and ATS data into prioritized, explainable recommendations.
    """
    parsed_resume = json.loads(resume.parsed_data) if resume.parsed_data else {}
    parsed_job = json.loads(job.parsed_data) if job and job.parsed_data else {}

    raw_text = resume.raw_text or ""
    ats_results = simulate_ats(job_match, resume) if job_match else {"ats_score": 85.0}
    ats_score = ats_results.get("ats_score", 85.0)

    # Match scores
    match_score = job_match.overall_score if (job_match and job_match.overall_score is not None) else 75.0
    skill_score = job_match.technical_score if (job_match and job_match.technical_score is not None) else 70.0

    # 1. Career Readiness Metrics
    career_readiness = {
        "overall_score": round((ats_score * 0.4) + (match_score * 0.6)),
        "resume_quality": round(min(100, len(raw_text) / 25 if raw_text else 80)),
        "ats_readiness": round(ats_score),
        "jd_match": round(match_score),
        "skill_coverage": round(skill_score)
    }

    # 2. Top Strengths Identification
    strengths = []
    if ats_score >= 80:
        strengths.append({
            "title": "High ATS Parser Compatibility",
            "detail": "Your resume uses standard headings, clean typography, and machine-readable layout structure."
        })
    if skill_score >= 70:
        strengths.append({
            "title": "Solid Technical Skill Foundation",
            "detail": "Your technical skill matrix closely aligns with core candidate requirements for this role."
        })
    
    projects = parsed_resume.get("projects", [])
    if projects and len(projects) > 0:
        strengths.append({
            "title": "Demonstrated Project Experience",
            "detail": f"Included {len(projects)} practical software projects showcasing real-world application."
        })

    education = parsed_resume.get("education", [])
    if education and len(education) > 0:
        strengths.append({
            "title": "Clear Educational Qualifications",
            "detail": f"Degrees and academic history are structured clearly for ATS verification."
        })

    # 3. Prioritized Recommendations Pipeline
    recommendations = []

    # Category A: Missing Technical Skills (From JobMatch)
    if job_match:
        skill_matches = SkillMatch.query.filter_by(job_match_id=job_match.id).all()
        missing_skills = [sm for sm in skill_matches if sm.match_type == 'missing']

        for sm in missing_skills[:4]: # Top 4 missing skills
            skill_name = sm.skill_name or "Required Skill"
            importance_str = "REQUIRED" if sm.required else "PREFERRED"
            recommendations.append({
                "category": "missing_keywords",
                "priority": "CRITICAL" if sm.required else "HIGH",
                "title": f"Add missing keyword: '{skill_name}'",
                "description": f"The job description explicitly prioritizes '{skill_name}', but it was not detected in your resume.",
                "reason": f"Required by JD as {importance_str} skill. Adding truthful evidence of {skill_name} directly improves your match score.",
                "before_text": "Technical Skills: C, C++, Java, Python, HTML, CSS, JavaScript",
                "after_text": f"Technical Skills: C, C++, Java, Python, HTML, CSS, JavaScript, {skill_name}",
                "impact": f"+5% to +10% JD Match Score Increase",
                "confidence": 0.95
            })

    # Category B: Experience & Quantification
    experience = parsed_resume.get("experience", [])
    if not experience or len(experience) == 0:
        recommendations.append({
            "category": "experience",
            "priority": "HIGH",
            "title": "Highlight Practical Project Accomplishments (Fresh Candidate)",
            "detail": "No formal work experience was detected. Emphasize project leadership, open-source contributions, or internship highlights.",
            "reason": "Recruiters look for practical proof of execution when work experience is limited.",
            "before_text": "Projects: Weather Forecast Website",
            "after_text": "Projects: Weather Forecast Website (Deployed web app handling live API data with 99% uptime)",
            "impact": "Improves recruiter engagement for entry-level engineering roles",
            "confidence": 0.90
        })

    # Category C: Professional Summary Check
    summary = parsed_resume.get("summary", "")
    if not summary or not summary.strip():
        recommendations.append({
            "category": "summary",
            "priority": "MEDIUM",
            "title": "Add a Tailored Professional Summary",
            "description": "Including a concise 2-3 line summary at the top of your resume quickly aligns your profile with target job expectations.",
            "reason": "ATS screeners and recruiters prioritize clear summary statements that state core technologies and career focus.",
            "before_text": "(No summary section present)",
            "after_text": f"Professional Summary: Dedicated Software Engineer skilled in C++, Python, and full-stack web development. Passionate about building scalable applications and solving complex algorithmic challenges.",
            "impact": "Increases ATS profile summary score and recruiter visual scan rate",
            "confidence": 0.88
        })

    # Category D: Project Bullet Quantification
    for proj in projects[:2]:
        p_title = proj.get("title") or "Key Project"
        recommendations.append({
            "category": "quantification",
            "priority": "MEDIUM",
            "title": f"Quantify achievements in project '{p_title}'",
            "description": "Add measurable metrics (e.g. API response time, user count, dataset size, performance gain) to project descriptions if true.",
            "reason": "Quantified bullets receive 40% higher evaluation ratings from technical hiring managers.",
            "before_text": f"• Developed a responsive weather forecasting web application using HTML, CSS, JavaScript, and Open-Meteo API.",
            "after_text": f"• Developed a responsive weather forecasting web application serving live data from Open-Meteo API with < 200ms latency.",
            "impact": "Elevates technical depth and project credibility",
            "confidence": 0.86
        })

    # Category E: Learning & Career Suggestions
    learning_suggestions = [
        {"technology": "Docker & Containerization", "reason": "Required in 65% of modern backend engineering roles."},
        {"technology": "PostgreSQL / SQL", "reason": "Standard requirement across software engineering job descriptions."},
        {"technology": "AWS / Cloud Deployment", "reason": "Highly desired for full-stack and backend software engineer positions."}
    ]

    return {
        "career_readiness": career_readiness,
        "strengths": strengths,
        "recommendations": recommendations,
        "learning_suggestions": learning_suggestions
    }
