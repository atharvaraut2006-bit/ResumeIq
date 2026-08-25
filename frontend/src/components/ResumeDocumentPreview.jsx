import React from 'react';
import './ResumeDocumentPreview.css';

const parseBulletParagraphs = (rawStr) => {
    if (!rawStr) return [];
    const str = String(rawStr);
    const rawLines = str.split('\n').map(l => l.trim()).filter(Boolean);
    const items = [];
    let currentItem = '';

    for (const line of rawLines) {
        const clean = line.replace(/^[•\-\*\s]+/, '').trim();
        if (!clean) continue;

        const isNewBullet = 
            /^[•\-\*]/.test(line) || 
            /^[\w\s&/()\-+]+:/.test(line) ||
            /^[A-Z][A-Za-z0-9\s&/()\-+]{2,40}(\s[–\-]\s|\s:|\()/i.test(line) ||
            /^(Tech Stack|Languages|Database|Software Engineering|Core Concepts|Web & Tools|Machine Learning|Agentic AI|Frameworks|Cloud)/i.test(line);

        if (isNewBullet && currentItem) {
            items.push(currentItem);
            currentItem = clean;
        } else if (!currentItem) {
            currentItem = clean;
        } else {
            currentItem += ' ' + clean;
        }
    }
    if (currentItem) {
        items.push(currentItem);
    }
    return items;
};

const KNOWN_HEADINGS_SET = new Set([
    "SUMMARY", "PROFESSIONAL SUMMARY", "PROFILE", "PROFILE SUMMARY", "ABOUT ME", "CAREER OBJECTIVE", "OBJECTIVE",
    "SKILLS", "TECHNICAL SKILLS", "CORE COMPETENCIES", "TECHNICAL PROFICIENCIES", "SKILLS & TECHNOLOGIES", "SKILLS TECHNOLOGIES",
    "EXPERIENCE", "WORK EXPERIENCE", "PROFESSIONAL EXPERIENCE", "EMPLOYMENT HISTORY", "INTERNSHIP", "INTERNSHIPS",
    "PROJECTS", "KEY PROJECTS", "ACADEMIC PROJECTS", "PERSONAL PROJECTS",
    "EDUCATION", "EDUCATION AND EXTRACURRICULAR", "EDUCATION & EXTRACURRICULAR", "ACADEMIC BACKGROUND",
    "CERTIFICATIONS", "CERTIFICATES", "LICENSES", "LICENSES & CERTIFICATIONS", "LICENSES AND CERTIFICATIONS",
    "ACHIEVEMENTS", "AWARDS", "HONORS", "PUBLICATIONS", "POSITIONS OF RESPONSIBILITY", "EXTRACURRICULAR ACTIVITIES", "EXTRACURRICULAR"
]);

const ResumeDocumentPreview = ({ 
    resumeData, 
    templateId = 'ats_focused', 
    sectionsOrder = ['summary', 'skills', 'experience', 'projects', 'education', 'certifications', 'achievements'], 
    includedSections = ['summary', 'skills', 'experience', 'projects', 'education', 'certifications', 'achievements'] 
}) => {
    if (!resumeData) return null;

    const contact = resumeData.contact || {};
    const name = contact.name || "Atharva Raviraj Raut";
    const email = contact.email || "";
    const phone = contact.phone || "";
    const linkedin = contact.linkedin || "";
    const github = contact.github || "";

    const contactParts = [phone, email, linkedin, github].filter(Boolean);

    const renderSectionContent = (secKey) => {
        if (!includedSections.includes(secKey)) return null;

        switch (secKey) {
            case 'summary': {
                const text = resumeData.summary;
                if (!text) return null;
                return (
                    <div key="summary" className="doc-section">
                        <h4 className="doc-heading">PROFESSIONAL SUMMARY</h4>
                        <p className="doc-body">{text}</p>
                    </div>
                );
            }

            case 'skills': {
                const skillsRaw = resumeData.skills_raw;
                const skillsList = resumeData.skills;
                let items = [];

                if (skillsRaw) {
                    items = parseBulletParagraphs(skillsRaw).filter(item => {
                        const clean = item.trim().toLowerCase();
                        if (clean.startsWith('pre-final year') || clean.startsWith('passionate about') || clean.startsWith('experienced in building')) {
                            return false;
                        }
                        return true;
                    });
                }

                // Extract all skill tokens already present in skillsRaw items
                const existingTokens = new Set();
                items.forEach(item => {
                    const text = item.includes(':') ? item.split(/:(.+)/)[1] || item : item;
                    text.toLowerCase().split(/[,|•]/).forEach(s => {
                        const clean = s.trim().toLowerCase();
                        if (clean) existingTokens.add(clean);
                    });
                });

                // Check skillsList for new user-added or confirmed skills
                let extraSkills = [];
                if (Array.isArray(skillsList)) {
                    skillsList.forEach(s => {
                        const name = typeof s === 'object' ? (s.canonical_name || s.skill_name || String(s)) : String(s);
                        if (name && !existingTokens.has(name.trim().toLowerCase())) {
                            extraSkills.push(name.trim());
                        }
                    });
                } else if (typeof skillsList === 'string' && skillsList.trim()) {
                    skillsList.split(',').forEach(s => {
                        const name = s.trim();
                        if (name && !existingTokens.has(name.toLowerCase())) {
                            extraSkills.push(name);
                        }
                    });
                }

                if (extraSkills.length > 0) {
                    items.push(`Additional Verified Skills: ${extraSkills.join(', ')}`);
                }

                if (items.length === 0 && skillsList) {
                    if (Array.isArray(skillsList)) {
                        items.push(skillsList.map(s => (typeof s === 'object' ? (s.canonical_name || s.skill_name || String(s)) : String(s))).join(', '));
                    } else {
                        items.push(String(skillsList));
                    }
                }

                if (items.length === 0) return null;

                return (
                    <div key="skills" className="doc-section">
                        <h4 className="doc-heading">TECHNICAL SKILLS</h4>
                        <div className="doc-skills-list">
                            {items.map((item, idx) => {
                                if (item.includes(':')) {
                                    const parts = item.split(/:(.+)/);
                                    const cat = parts[0];
                                    const val = parts[1] || '';
                                    return (
                                        <p key={idx} className="doc-bullet">
                                            • <strong>{cat.trim()}:</strong> {val.trim()}
                                        </p>
                                    );
                                }
                                return <p key={idx} className="doc-bullet">• {item}</p>;
                            })}
                        </div>
                    </div>
                );
            }

            case 'experience': {
                const expList = resumeData.experience || [];
                if (!expList || expList.length === 0) return null;
                return (
                    <div key="experience" className="doc-section">
                        <h4 className="doc-heading">WORK EXPERIENCE</h4>
                        {expList.map((e, idx) => {
                            const eText = e.raw || e.description || "";
                            if (!eText) return null;
                            const bullets = parseBulletParagraphs(eText);
                            return bullets.map((cleanText, bIdx) => (
                                <p key={`${idx}-${bIdx}`} className="doc-bullet">• {cleanText}</p>
                            ));
                        })}
                    </div>
                );
            }

            case 'projects': {
                const projList = resumeData.projects || [];
                if (!projList || projList.length === 0) return null;
                return (
                    <div key="projects" className="doc-section">
                        <h4 className="doc-heading">PROJECTS</h4>
                        {projList.map((p, idx) => {
                            const pName = p.name && p.name !== "Key Project" ? p.name : null;
                            const pDesc = p.raw || p.description || "";
                            const bullets = parseBulletParagraphs(pDesc);
                            return (
                                <div key={idx} className="doc-project-block">
                                    {pName && <div className="doc-project-title">{pName}</div>}
                                    {bullets.map((cleanB, bIdx) => (
                                        <p key={bIdx} className="doc-bullet">• {cleanB}</p>
                                    ))}
                                </div>
                            );
                        })}
                    </div>
                );
            }

            case 'education': {
                const eduList = resumeData.education || [];
                if (!eduList || eduList.length === 0) return null;
                return (
                    <div key="education" className="doc-section">
                        <h4 className="doc-heading">EDUCATION</h4>
                        {eduList.map((e, idx) => {
                            const eText = e.raw || `${e.degree || ''} - ${e.institution || ''}`;
                            const bullets = parseBulletParagraphs(eText);
                            return bullets.map((cleanText, bIdx) => (
                                <p key={`${idx}-${bIdx}`} className="doc-bullet">• {cleanText}</p>
                            ));
                        })}
                    </div>
                );
            }

            case 'certifications': {
                const certList = resumeData.certifications || [];
                if (!certList || certList.length === 0) return null;
                return (
                    <div key="certifications" className="doc-section">
                        <h4 className="doc-heading">CERTIFICATIONS</h4>
                        {certList.map((c, idx) => {
                            const cText = c.raw || c.name || String(c);
                            const cleanText = cText.replace(/^[•\-\*\s]+/, '').trim();
                            return <p key={idx} className="doc-bullet">• {cleanText}</p>;
                        })}
                    </div>
                );
            }

            case 'achievements': {
                const achList = resumeData.achievements || [];
                if (!achList || achList.length === 0) return null;
                return (
                    <div key="achievements" className="doc-section">
                        <h4 className="doc-heading">ACHIEVEMENTS</h4>
                        {achList.map((a, idx) => {
                            const aText = a.raw || String(a);
                            const cleanText = aText.replace(/^[•\-\*\s]+/, '').trim();
                            return <p key={idx} className="doc-bullet">• {cleanText}</p>;
                        })}
                    </div>
                );
            }

            default:
                return null;
        }
    };

    return (
        <div className={`doc-preview-paper template-${templateId}`}>
            {/* Header */}
            <div className="doc-header">
                <h1 className="doc-name">{name.toUpperCase()}</h1>
                {contactParts.length > 0 && (
                    <div className="doc-contact-line">
                        {contactParts.join('  •  ')}
                    </div>
                )}
                <div className="doc-divider"></div>
            </div>

            {/* Sections in user-specified order */}
            <div className="doc-body-content">
                {resumeData.raw_text && !resumeData.is_edited ? (
                    String(resumeData.raw_text).split('\n').map(l => l.trim()).filter(Boolean).map((line, idx) => {
                        const cleanLine = line.replace(/^[•\-\*\s]+/, '').trim();
                        const lower = cleanLine.toLowerCase();
                        
                        // Skip header info if already in contact bar
                        if (email && lower.includes(email.toLowerCase())) return null;
                        if (phone && lower.replace(/[-.\s]/g, '').includes(phone.replace(/[-.\s]/g, ''))) return null;
                        if (name && lower.includes(name.toLowerCase())) return null;
                        if (lower === 'linkedin' || lower === 'github' || lower.includes('linkedin.com') || lower.includes('github.com')) return null;

                        const cleanHeadingCheck = cleanLine.replace(/[^A-Za-z0-9\s&]/g, '').trim().toUpperCase();
                        const isHeading = KNOWN_HEADINGS_SET.has(cleanHeadingCheck);

                        if (isHeading) {
                            return (
                                <div key={idx} className="doc-section" style={{ marginTop: '0.8rem' }}>
                                    <h4 className="doc-heading">{cleanLine.toUpperCase()}</h4>
                                </div>
                            );
                        }

                        if (/^[•\-\*]/.test(line) || /^(Tech Stack|Languages|Database|Software Engineering|Core Concepts|Web & Tools|Machine Learning|Agentic AI|Frameworks|Cloud):/i.test(cleanLine)) {
                            if (cleanLine.includes(':')) {
                                const parts = cleanLine.split(/:(.+)/);
                                const cat = parts[0];
                                const val = parts[1] || '';
                                return (
                                    <p key={idx} className="doc-bullet">
                                        • <strong>{cat.trim()}:</strong> {val.trim()}
                                    </p>
                                );
                            }
                            return <p key={idx} className="doc-bullet">• {cleanLine}</p>;
                        }

                        return <p key={idx} className="doc-body">{cleanLine}</p>;
                    })
                ) : (
                    sectionsOrder.map(secKey => renderSectionContent(secKey))
                )}
            </div>
        </div>
    );
};

export default ResumeDocumentPreview;
