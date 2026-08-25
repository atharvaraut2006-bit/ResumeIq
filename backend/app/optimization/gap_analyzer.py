from app.models.job_match import JobMatch, SkillMatch

def analyze_gaps(job_match: JobMatch):
    """
    Phase 8: Skill Gap Analysis & Priority Ranking.
    Consumes Phase 7 output.
    """
    skill_matches = SkillMatch.query.filter_by(job_match_id=job_match.id).all()
    
    high_priority = []
    medium_priority = []
    low_priority = []
    
    soft_skill_gaps = []
    weak_evidence = []
    
    CLOUD_DEVOPS_SKILLS = {'aws', 'azure', 'google cloud', 'gcp', 'docker', 'kubernetes', 'ci/cd', 'terraform', 'jenkins', 'devops'}
    TOOL_GENERAL_SKILLS = {'dbms', 'software engineering', 'git', 'github', 'jira', 'figma', 'postman', 'agile', 'scrum', 'operating systems', 'computer networks'}

    missing_gaps = []
    for sm in skill_matches:
        if sm.match_type == "missing":
            gap = {
                "skill": sm.skill_name,
                "required": sm.required,
                "confidence": 95,
                "reason": f"Required technical skill missing from resume.",
                "action": f"If you have {sm.skill_name} experience, add it to your Skills section.",
                "category": sm.category
            }
            missing_gaps.append(gap)

    for gap in missing_gaps:
        sname = gap["skill"].lower()
        if sname in CLOUD_DEVOPS_SKILLS or gap["category"] == "soft":
            gap["priority"] = "moderate"
            medium_priority.append(gap)
        elif sname in TOOL_GENERAL_SKILLS or not gap["required"]:
            gap["priority"] = "low"
            low_priority.append(gap)
        else:
            gap["priority"] = "high"
            high_priority.append(gap)

    # Balance distribution if high_priority is over-saturated (> 4)
    if len(high_priority) > 4:
        overflow = high_priority[4:]
        high_priority = high_priority[:4]
        for idx, item in enumerate(overflow):
            if idx % 2 == 0:
                item["priority"] = "moderate"
                medium_priority.append(item)
            else:
                item["priority"] = "low"
                low_priority.append(item)
                
        elif sm.match_type == "semantic" and sm.category == "soft":
            if sm.confidence and sm.confidence < 0.80:
                weak_evidence.append({
                    "skill": sm.skill_name,
                    "evidence_found": sm.evidence,
                    "reason": f"Limited evidence for {sm.skill_name} detected.",
                    "action": f"Strengthen the phrasing to clearly demonstrate {sm.skill_name}.",
                    "priority": "low"
                })
                
    # Add non-skill gaps
    experience_gaps = []
    if job_match.experience_score is not None and job_match.experience_score < 100:
        experience_gaps.append("Experience falls short of requirements. Focus on demonstrating rapid impact in existing roles.")
        
    education_gaps = []
    if job_match.education_score is not None and job_match.education_score < 100:
        education_gaps.append("Missing preferred degree level. Emphasize relevant certifications or real-world project complexity.")
        
    project_gaps = []
    if job_match.project_score is not None and job_match.project_score < 50:
        project_gaps.append("Projects lack direct relevance to the JD requirements. Consider building a domain-specific project.")

    # Roadmap
    learning_roadmap = []
    step = 1
    for h in high_priority[:3]:
        learning_roadmap.append(f"Step {step}: Learn {h['skill']} fundamentals.")
        step += 1
    if learning_roadmap:
        learning_roadmap.append(f"Step {step}: Build a small project demonstrating the above skills.")

    return {
        "skill_gaps": {
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "low_priority": low_priority
        },
        "soft_skill_gaps": soft_skill_gaps,
        "weak_evidence": weak_evidence,
        "experience_gaps": experience_gaps,
        "education_gaps": education_gaps,
        "project_gaps": project_gaps,
        "learning_roadmap": learning_roadmap
    }
