import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf(
    resume_data: dict,
    output_path: str,
    template_id: str = "ats_focused",
    sections_order: list = None,
    included_sections: list = None
) -> dict:
    """
    Generates a professional, searchable, ATS-friendly PDF resume using ReportLab.
    Supports template_id: 'ats_focused', 'classic_professional', 'modern_minimal', 'technical'.
    """
    if sections_order is None:
        sections_order = ['summary', 'skills', 'experience', 'projects', 'education', 'certifications', 'achievements']
    if included_sections is None:
        included_sections = ['summary', 'skills', 'experience', 'projects', 'education', 'certifications', 'achievements']

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36, # 0.5 inch margins
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Template Color & Typography Variations
    if template_id == 'classic_professional':
        font_main = 'Times-Roman'
        font_bold = 'Times-Bold'
        primary_color = colors.HexColor('#1f2937')
        accent_color = colors.HexColor('#1e40af')
    elif template_id == 'modern_minimal':
        font_main = 'Helvetica'
        font_bold = 'Helvetica-Bold'
        primary_color = colors.HexColor('#0f172a')
        accent_color = colors.HexColor('#0d9488')
    elif template_id == 'technical':
        font_main = 'Courier'
        font_bold = 'Courier-Bold'
        primary_color = colors.HexColor('#18181b')
        accent_color = colors.HexColor('#4f46e5')
    else: # ats_focused
        font_main = 'Helvetica'
        font_bold = 'Helvetica-Bold'
        primary_color = colors.HexColor('#111827')
        accent_color = colors.HexColor('#2563eb')

    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle',
        fontName=font_bold,
        fontSize=20,
        leading=24,
        textColor=primary_color,
        alignment=1, # Center
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        fontName=font_main,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#4b5563'),
        alignment=1, # Center
        spaceAfter=10
    )

    heading_style = ParagraphStyle(
        'DocHeading',
        fontName=font_bold,
        fontSize=12,
        leading=15,
        textColor=accent_color,
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'DocBody',
        fontName=font_main,
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'DocBullet',
        fontName=font_main,
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#374151'),
        leftIndent=12,
        spaceAfter=3
    )

    story = []

    # 1. Contact Header
    contact = resume_data.get('contact', {})
    name = contact.get('name') or "Atharva Raviraj Raut"
    email = contact.get('email') or ""
    phone = contact.get('phone') or ""
    linkedin = contact.get('linkedin') or ""
    github = contact.get('github') or ""

    story.append(Paragraph(name.upper(), title_style))

    contact_parts = [p for p in [phone, email, linkedin, github] if p]
    if contact_parts:
        contact_line = "  •  ".join(contact_parts)
        story.append(Paragraph(contact_line, subtitle_style))

    story.append(HRFlowable(width="100%", thickness=1, color=accent_color, spaceAfter=8))

    # Helper function to render sections
    def render_section(section_key):
        if section_key not in included_sections:
            return

        if section_key == 'summary':
            summary_text = resume_data.get('summary')
            if summary_text:
                story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
                story.append(Paragraph(summary_text, body_style))
                story.append(Spacer(1, 4))

        elif section_key == 'skills':
            skills_raw = resume_data.get('skills_raw')
            skills_list = resume_data.get('skills')
            items = []
            
            if skills_raw:
                items = [i.strip() for i in str(skills_raw).replace('\n', '•').split('•') if i.strip()]
                
            existing_tokens = set()
            for item in items:
                text = item.split(':', 1)[1] if ':' in item else item
                for s in text.lower().replace('|', ',').split(','):
                    if s.strip():
                        existing_tokens.add(s.strip())
                        
            extra_skills = []
            if isinstance(skills_list, list):
                for s in skills_list:
                    name = s.get('canonical_name') or s.get('skill_name') or str(s) if isinstance(s, dict) else str(s)
                    if name and name.strip().lower() not in existing_tokens:
                        extra_skills.append(name.strip())
            elif isinstance(skills_list, str) and skills_list.strip():
                for s in skills_list.split(','):
                    if s.strip() and s.strip().lower() not in existing_tokens:
                        extra_skills.append(s.strip())
                        
            if extra_skills:
                items.append(f"Additional Verified Skills: {', '.join(extra_skills)}")
                
            if not items and skills_list:
                items = [", ".join([s.get('canonical_name', str(s)) if isinstance(s, dict) else str(s) for s in skills_list]) if isinstance(skills_list, list) else str(skills_list)]
                
            if items:
                story.append(Paragraph("TECHNICAL SKILLS", heading_style))
                for item in items:
                    if ':' in item:
                        cat, val = item.split(':', 1)
                        formatted_item = f"<b>{cat.strip()}:</b> {val.strip()}"
                    else:
                        formatted_item = item
                    story.append(Paragraph(f"• {formatted_item}", bullet_style))
                story.append(Spacer(1, 4))

        elif section_key == 'experience':
            exp_list = resume_data.get('experience', [])
            if exp_list:
                story.append(Paragraph("WORK EXPERIENCE", heading_style))
                for exp in exp_list:
                    exp_text = exp.get('raw') or exp.get('description') or ""
                    if exp_text:
                        clean_exp = re.sub(r'^[•\-\*\s]+', '', exp_text).strip()
                        story.append(Paragraph(f"• {clean_exp}", bullet_style))
                story.append(Spacer(1, 4))

        elif section_key == 'projects':
            proj_list = resume_data.get('projects', [])
            if proj_list:
                story.append(Paragraph("PROJECTS", heading_style))
                for proj in proj_list:
                    p_name = proj.get('name') or "Key Project"
                    p_desc = proj.get('raw') or proj.get('description') or ""
                    story.append(Paragraph(f"<b>{p_name}</b>", body_style))
                    if p_desc:
                        bullets = [b.strip() for b in p_desc.split('\n') if b.strip()]
                        for b in bullets:
                            clean_b = re.sub(r'^[•\-\*\s]+', '', b).strip()
                            story.append(Paragraph(f"• {clean_b}", bullet_style))
                story.append(Spacer(1, 4))

        elif section_key == 'education':
            edu_list = resume_data.get('education', [])
            if edu_list:
                story.append(Paragraph("EDUCATION", heading_style))
                for edu in edu_list:
                    e_text = edu.get('raw') or f"{edu.get('degree', '')} - {edu.get('institution', '')}"
                    if e_text:
                        clean_e = re.sub(r'^[•\-\*\s]+', '', e_text).strip()
                        story.append(Paragraph(f"• {clean_e}", bullet_style))
                story.append(Spacer(1, 4))

        elif section_key == 'certifications':
            cert_list = resume_data.get('certifications', [])
            if cert_list:
                story.append(Paragraph("CERTIFICATIONS", heading_style))
                for c in cert_list:
                    c_text = c.get('raw') or c.get('name') or str(c)
                    if c_text:
                        clean_c = re.sub(r'^[•\-\*\s]+', '', c_text).strip()
                        story.append(Paragraph(f"• {clean_c}", bullet_style))
                story.append(Spacer(1, 4))

        elif section_key == 'achievements':
            ach_list = resume_data.get('achievements', [])
            if ach_list:
                story.append(Paragraph("ACHIEVEMENTS", heading_style))
                for a in ach_list:
                    a_text = a.get('raw') or str(a)
                    if a_text:
                        clean_a = re.sub(r'^[•\-\*\s]+', '', a_text).strip()
                        story.append(Paragraph(f"• {clean_a}", bullet_style))
                story.append(Spacer(1, 4))

    # Render sections according to requested order
    for sec in sections_order:
        render_section(sec)

    doc.build(story)

    # Calculate estimated page count
    estimated_pages = 1 if len(story) < 35 else 2

    return {
        "output_path": output_path,
        "page_count": estimated_pages
    }
