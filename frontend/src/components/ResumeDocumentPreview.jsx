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
                    items = parseBulletParagraphs(skillsRaw);
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
                            const pName = p.name || "Key Project";
                            const pDesc = p.raw || p.description || "";
                            const bullets = parseBulletParagraphs(pDesc);
                            return (
                                <div key={idx} className="doc-project-block">
                                    <div className="doc-project-title">{pName}</div>
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
                            const cleanText = eText.replace(/^[•\-\*\s]+/, '').trim();
                            return <p key={idx} className="doc-bullet">• {cleanText}</p>;
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
                {sectionsOrder.map(secKey => renderSectionContent(secKey))}
            </div>
        </div>
    );
};

export default ResumeDocumentPreview;
