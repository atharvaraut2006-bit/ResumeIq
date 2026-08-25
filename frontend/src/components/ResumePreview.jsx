import React from 'react';
import './ResumePreview.css';

const ResumePreview = ({ data, skills, filename, onReset }) => {
    if (!data) return null;

    const { contact, education, experience, projects, certifications } = data;

    // Group skills by category
    const skillsByCategory = skills?.reduce((acc, rs) => {
        const cat = rs.skill.category || 'Other';
        if (!acc[cat]) acc[cat] = [];
        acc[cat].push(rs);
        return acc;
    }, {});

    return (
        <div className="preview-container">
            <h3>Resume: {filename}</h3>
            <hr />
            
            <div className="preview-section">
                <h4>Detected Information</h4>
                
                <div className="info-block">
                    <strong>Name:</strong>
                    <p>{contact?.name || 'Not detected'}</p>
                </div>
                
                <div className="info-block">
                    <strong>Email:</strong>
                    <p>{contact?.email || 'Not detected'}</p>
                </div>

                <div className="info-block">
                    <strong>Education:</strong>
                    {education && education.length > 0 ? (
                        education.map((edu, idx) => (
                            <p key={idx} className="pre-wrap">{edu.raw.trim()}</p>
                        ))
                    ) : (
                        <p>Not detected</p>
                    )}
                </div>

                <div className="info-block">
                    <strong>Projects:</strong>
                    <p>{projects ? `${projects.length} detected` : 'Not detected'}</p>
                </div>

                <div className="info-block">
                    <strong>Experience:</strong>
                    <p>{experience ? `${experience.length} entry detected` : 'Not detected'}</p>
                </div>
                
                <hr />
                <h4>Detected Skills</h4>
                
                {skillsByCategory && Object.keys(skillsByCategory).length > 0 ? (
                    Object.entries(skillsByCategory)
                        .filter(([category]) => category !== "Version Control")
                        .map(([category, catSkills]) => (
                            <div key={category} className="skill-category">
                                <h5>{category}</h5>
                                <ul>
                                    {catSkills.map((rs, idx) => (
                                        <li key={idx}>
                                            <span className="skill-name-plain">{rs.skill.canonical_name}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))
                ) : (
                    <p>No skills detected.</p>
                )}
            </div>

            {onReset && (
                <div className="preview-footer">
                    <button className="reset-btn-contained" onClick={onReset}>
                        Start Over (New Resume)
                    </button>
                </div>
            )}
        </div>
    );
};

export default ResumePreview;
