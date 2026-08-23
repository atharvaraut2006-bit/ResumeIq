import React from 'react';
import './JobPreview.css';

const JobPreview = ({ data }) => {
    if (!data) return null;

    const { 
        title, company, required_skills, preferred_skills, 
        experience_requirements, education_requirements, 
        responsibilities, soft_skills 
    } = data;

    return (
        <div className="preview-container job-preview">
            <h3>Job Description Analysis</h3>
            <hr />
            
            <div className="preview-section">
                
                {(title || company) && (
                    <div className="info-block">
                        <strong>Role:</strong>
                        <p>{title || 'Unknown Title'} {company ? `at ${company}` : ''}</p>
                    </div>
                )}

                <div className="info-block">
                    <strong>Required Skills</strong>
                    {required_skills && required_skills.length > 0 ? (
                        <ul className="skill-list req-list">
                            {required_skills.map((rs, idx) => (
                                <li key={idx}>✓ {rs.skill.canonical_name} <span className="meta">({(rs.confidence*100).toFixed(0)}%)</span></li>
                            ))}
                        </ul>
                    ) : <p>None detected</p>}
                </div>

                <div className="info-block">
                    <strong>Preferred Skills</strong>
                    {preferred_skills && preferred_skills.length > 0 ? (
                        <ul className="skill-list pref-list">
                            {preferred_skills.map((rs, idx) => (
                                <li key={idx}>○ {rs.skill.canonical_name} <span className="meta">({(rs.confidence*100).toFixed(0)}%)</span></li>
                            ))}
                        </ul>
                    ) : <p>None detected</p>}
                </div>

                <div className="info-block">
                    <strong>Experience</strong>
                    {experience_requirements && experience_requirements.length > 0 ? (
                        <ul>
                            {experience_requirements.map((exp, idx) => (
                                <li key={idx}>{exp.raw_text}</li>
                            ))}
                        </ul>
                    ) : <p>Not specified</p>}
                </div>

                <div className="info-block">
                    <strong>Education</strong>
                    {education_requirements && education_requirements.length > 0 ? (
                        <ul>
                            {education_requirements.map((edu, idx) => (
                                <li key={idx}>{edu.degree}</li>
                            ))}
                        </ul>
                    ) : <p>Not specified</p>}
                </div>

                <div className="info-block">
                    <strong>Responsibilities</strong>
                    {responsibilities && responsibilities.length > 0 ? (
                        <ul className="resp-list">
                            {responsibilities.map((resp, idx) => (
                                <li key={idx}>• {resp}</li>
                            ))}
                        </ul>
                    ) : <p>Not detected</p>}
                </div>

                <div className="info-block">
                    <strong>Soft Skills</strong>
                    {soft_skills && soft_skills.length > 0 ? (
                        <ul className="resp-list">
                            {soft_skills.map((ss, idx) => (
                                <li key={idx}>• {ss}</li>
                            ))}
                        </ul>
                    ) : <p>None detected</p>}
                </div>
            </div>
        </div>
    );
};

export default JobPreview;
