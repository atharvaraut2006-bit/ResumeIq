import json
import copy
from app import db
from app.models.resume import Resume
from app.models.job import Job
from app.models.job_match import JobMatch, SkillMatch
from app.models.optimization import ResumeVersion, ResumeChange
from app.optimization.fact_checker import verify_factuality
from app.optimization.rewriter import STRONG_VERBS, WEAK_VERBS

def generate_optimized_resume_version(
    resume_id: int, 
    job_id: int, 
    mode: str = 'balanced',
    sections_to_optimize: list = None,
    confirmed_skills: list = None
) -> ResumeVersion:
    """
    Phase 10: Generates a JD-specific optimized resume draft without modifying the original.
    Creates structured ResumeChange objects for review.
    """
    resume = Resume.query.get(resume_id)
    job = Job.query.get(job_id)
    job_match = JobMatch.query.filter_by(resume_id=resume_id, job_id=job_id).first()
    
    if not resume or not job or not job_match:
        raise ValueError("Resume, Job, or JobMatch not found")
        
    sections_to_optimize = sections_to_optimize or ['summary', 'skills', 'experience', 'projects']
    confirmed_skills = confirmed_skills or []
    
    try:
        parsed_original = json.loads(resume.parsed_data or '{}')
    except Exception:
        parsed_original = {}
        
    parsed_optimized = copy.deepcopy(parsed_original)
    
    # Check current versions count to generate Version Number & Name
    existing_versions_count = ResumeVersion.query.filter_by(resume_id=resume_id).count()
    version_num = existing_versions_count + 1
    company_name = getattr(job, 'company', None) or getattr(job, 'company_name', None) or 'Target Role'
    version_name = f"Resume — {job.title or 'Job'} ({company_name})"
    
    new_version = ResumeVersion(
        resume_id=resume_id,
        job_match_id=job_match.id,
        version_number=version_num,
        version_name=version_name,
        optimization_mode=mode,
        status='draft',
        parsed_data=json.dumps(parsed_optimized),
        original_match_score=job_match.overall_score,
        original_ats_score=job_match.overall_score * 0.9
    )
    db.session.add(new_version)
    db.session.flush() # Get new_version.id
    
    skill_matches = SkillMatch.query.filter_by(job_match_id=job_match.id).all()
    jd_skills = [sm.skill_name.lower() for sm in skill_matches]
    matched_tech = [sm.skill_name for sm in skill_matches if sm.match_type in ['exact', 'normalized', 'semantic'] and getattr(sm, 'category', '') != 'soft']
    tech_str = ", ".join(matched_tech[:5]) if matched_tech else "software engineering & technical analysis"
    
    # Extract missing soft skills & required components from JobMatch
    missing_soft_skills = [sm.skill_name for sm in skill_matches if getattr(sm, 'category', '') == 'soft' and sm.match_type == 'missing']
    soft_str = ", ".join(missing_soft_skills[:3]) if missing_soft_skills else "analytical problem-solving, collaboration, and clear technical communication"

    # Exceptional Resume Guardrail (Score >= 96%)
    if job_match.overall_score >= 96.0:
        new_version.parsed_data = json.dumps(parsed_optimized)
        db.session.commit()
        return new_version

    # 1. Summary Optimization
    if 'summary' in sections_to_optimize:
        orig_summary = parsed_original.get('summary', '').strip()
        new_summary = f"{orig_summary} Specialized in {tech_str} with strong focus on {soft_str} aligned with {job.title or 'the role'}." if orig_summary else f"Motivated candidate skilled in {tech_str}, demonstrating {soft_str} aligned with {job.title or 'the target role'}."
            
        parsed_optimized['summary'] = new_summary
        db.session.add(ResumeChange(
            version_id=new_version.id,
            section='summary',
            original_text=orig_summary if orig_summary else "(No summary section found in original resume)",
            new_text=new_summary,
            change_type='summary_update',
            reason=f"Structured professional summary emphasizing core target skills ({tech_str}) and key soft skill competencies ({soft_str}).",
            impact='High'
        ))

    # 2. Skills Section Optimization & Reorganization (Only Yes or Unsure confirmed skills)
    if 'skills' in sections_to_optimize:
        orig_skills_raw = parsed_original.get('skills') or parsed_original.get('technical_skills') or []
        if isinstance(orig_skills_raw, list):
            orig_skills_list = [str(s) for s in orig_skills_raw]
            orig_skills_str = ", ".join(orig_skills_list)
        else:
            orig_skills_str = str(orig_skills_raw)
            orig_skills_list = [s.strip() for s in orig_skills_str.split(',') if s.strip()]

        # Only add confirmed skills (Yes or Unsure) + missing soft skills
        combined_skills = list(set(orig_skills_list + confirmed_skills + missing_soft_skills[:2]))
        prioritized_skills = sorted(combined_skills, key=lambda s: 0 if s.lower() in jd_skills else 1)
        new_skills_str = ", ".join(prioritized_skills)

        parsed_optimized['skills'] = prioritized_skills
        db.session.add(ResumeChange(
            version_id=new_version.id,
            section='skills',
            original_text=orig_skills_str if orig_skills_str else "(No technical skills detected in original resume)",
            new_text=new_skills_str,
            change_type='skill_reorganization',
            reason=f"Reorganized skills to prioritize Job Description requirements, incorporating confirmed skills ({', '.join(confirmed_skills) if confirmed_skills else 'Yes/Unsure confirmed'}) and key required soft skills ({', '.join(missing_soft_skills[:2]) if missing_soft_skills else 'soft skills'}).",
            impact='High'
        ))

    # 3. Project 1 Enhancement
    projects = parsed_optimized.get('projects', [])
    if 'projects' in sections_to_optimize and len(projects) > 0:
        p0 = projects[0]
        orig_p0_desc = p0.get('description') or p0.get('title') or ''
        orig_p0_title = p0.get('title') or 'Technical Project'
        
        new_p0_desc = f"Architected and deployed {orig_p0_title} incorporating {tech_str[:35]}. Optimized performance and established clear component architecture for high reliability."
        p0['description'] = new_p0_desc
        
        db.session.add(ResumeChange(
            version_id=new_version.id,
            section='projects',
            original_text=orig_p0_desc if orig_p0_desc else f"Project: {orig_p0_title}",
            new_text=new_p0_desc,
            change_type='rewrite',
            reason=f"Enhanced {orig_p0_title} project description with active technical verbs and architecture context.",
            impact='High'
        ))

    # 4. Project 2 / Project Enhancement
    if 'projects' in sections_to_optimize and len(projects) > 1:
        p1 = projects[1]
        orig_p1_desc = p1.get('description') or p1.get('title') or ''
        orig_p1_title = p1.get('title') or 'Key Project'
        
        new_p1_desc = f"Engineered {orig_p1_title} utilizing clean coding patterns, responsive UI design, and modular backend API integration."
        p1['description'] = new_p1_desc
        
        db.session.add(ResumeChange(
            version_id=new_version.id,
            section='projects',
            original_text=orig_p1_desc if orig_p1_desc else f"Project: {orig_p1_title}",
            new_text=new_p1_desc,
            change_type='rewrite',
            reason=f"Refined {orig_p1_title} to demonstrate backend API integration and modular development standards.",
            impact='Medium'
        ))

    # 5. Education & Coursework Formatting
    if 'education' in sections_to_optimize:
        edu_raw = parsed_optimized.get('education', [])
        if isinstance(edu_raw, list) and len(edu_raw) > 0:
            edu0 = edu_raw[0]
            if isinstance(edu0, dict):
                orig_edu_text = f"{edu0.get('degree', 'Degree')} - {edu0.get('institution', 'University')} ({edu0.get('year', 'Recent')})"
                if edu0.get('gpa'): orig_edu_text += f" [CGPA/GPA: {edu0.get('gpa')}]"
            else:
                orig_edu_text = str(edu0)
            
            new_edu_text = f"{orig_edu_text} | Key Coursework: Data Structures, Algorithms, Software Engineering, Database Systems."
            
            db.session.add(ResumeChange(
                version_id=new_version.id,
                section='education',
                original_text=orig_edu_text,
                new_text=new_edu_text,
                change_type='formatting',
                reason="Added relevant computer science & engineering coursework keywords for ATS education section parsing.",
                impact='Medium'
            ))

    # 6. Certifications & Achievements Optimization
    if 'certifications' in sections_to_optimize:
        certs_raw = parsed_optimized.get('certifications', []) or parsed_optimized.get('achievements', [])
        if isinstance(certs_raw, list) and len(certs_raw) > 0:
            orig_cert_str = ", ".join([str(c.get('name') if isinstance(c, dict) else c) for c in certs_raw[:3]])
            new_cert_str = f"{orig_cert_str} (Verified Technical Knowledge & Excellence)"
            
            db.session.add(ResumeChange(
                version_id=new_version.id,
                section='certifications',
                original_text=orig_cert_str,
                new_text=new_cert_str,
                change_type='formatting',
                reason="Standardized certification titles for machine-readable verification.",
                impact='Low'
            ))

    new_version.parsed_data = json.dumps(parsed_optimized)
    db.session.commit()
    
    return new_version
