import React from 'react';
import './ResumeDocumentPreview.css';

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
                const skillsRaw = resumeData.skills_raw || resumeData.skills;
                if (!skillsRaw) return null;
                let skillsText = "";
                if (Array.isArray(skillsRaw)) {
                    skillsText = skillsRaw.map(s => s.canonical_name || s.skill_name || String(s)).join(', ');
                } else {
                    skillsText = String(skillsRaw);
                }
                return (
                    <div key="skills" className="doc-section">
                        <h4 className="doc-heading">TECHNICAL SKILLS</h4>
                        <p className="doc-body">{skillsText}</p>
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
                            return <p key={idx} className="doc-bullet">• {eText.trim()}</p>;
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
                            const bullets = pDesc ? pDesc.split('\n').filter(b => b.trim()) : [];
                            return (
                                <div key={idx} className="doc-project-block">
                                    <div className="doc-project-title">{pName}</div>
                                    {bullets.map((b, bIdx) => (
                                        <p key={bIdx} className="doc-bullet">• {b.replace(/^[•\-\s]+/, '')}</p>
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
                            return <p key={idx} className="doc-bullet">• {eText.trim()}</p>;
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
                            return <p key={idx} className="doc-bullet">• {cText.trim()}</p>;
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
                            return <p key={idx} className="doc-bullet">• {aText.trim()}</p>;
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
