import React from 'react';
import './MatchResults.css';

const CircularScoreGauge = ({ targetScore, categoryText, label = "Overall Match", color = "green" }) => {
    const [displayScore, setDisplayScore] = React.useState(0);

    React.useEffect(() => {
        const duration = 1200; // 1.2s animation
        const startTime = performance.now();

        const animate = (now) => {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeProgress = 1 - Math.pow(1 - progress, 3);
            const current = easeProgress * targetScore;
            setDisplayScore(current);

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }, [targetScore]);

    const radius = 42;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (Math.min(100, displayScore) / 100) * circumference;
    const strokeColor = color === 'green' ? '#28a745' : color === 'orange' ? '#fd7e14' : '#dc3545';

    return (
        <div className="circular-gauge-wrapper">
            <svg width="125" height="125" viewBox="0 0 110 110">
                <circle
                    cx="55"
                    cy="55"
                    r={radius}
                    stroke="#e9ecef"
                    strokeWidth="9"
                    fill="transparent"
                />
                <circle
                    cx="55"
                    cy="55"
                    r={radius}
                    stroke={strokeColor}
                    strokeWidth="9"
                    fill="transparent"
                    strokeDasharray={circumference}
                    strokeDashoffset={strokeDashoffset}
                    strokeLinecap="round"
                    transform="rotate(-90 55 55)"
                />
            </svg>
            <div className="gauge-center-content">
                <span className="gauge-label">{label}</span>
                <span className="gauge-score-val" style={{ color: strokeColor }}>
                    {displayScore.toFixed(1)} / 100
                </span>
                <span className="gauge-cat-text" style={{ color: strokeColor }}>
                    {categoryText.toUpperCase()}
                </span>
            </div>
        </div>
    );
};

const MatchResults = ({ matchData, onAnalyzeAnother }) => {
    if (!matchData) return null;

    const {
        overall_score,
        score_category,
        technical_score,
        soft_skill_score,
        experience_score,
        responsibility_score,
        project_score,
        education_score,
        preferred_skill_score,
        certification_score,
        matched_skills,
        matched_soft_skills,
        missing_required_skills,
        missing_preferred_skills,
        related_skills,
        explanations,
        job
    } = matchData;

    const scoreColor = overall_score >= 80 ? 'green' : overall_score >= 60 ? 'orange' : 'red';

    const renderScoreBar = (label, score) => {
        if (score === null || score === undefined) {
            return (
                <div className="score-bar-container">
                    <div className="score-bar-label">
                        <span>{label}</span>
                        <span className="score-na-badge">N/A (Not Specified in JD)</span>
                    </div>
                    <div className="score-bar-track">
                        <div className="score-bar-fill" style={{ width: '0%', backgroundColor: '#e9ecef' }}></div>
                    </div>
                </div>
            );
        }

        const width = Math.min(100, Math.max(0, score));
        const rounded = Math.round(score);
        const barColor = rounded >= 70 ? '#28a745' : rounded >= 40 ? '#007bff' : '#dc3545';

        return (
            <div className="score-bar-container">
                <div className="score-bar-label">
                    <span>{label}</span>
                    <span className="score-pct-val" style={{ color: barColor }}>{rounded}%</span>
                </div>
                <div className="score-bar-track">
                    <div className="score-bar-fill" style={{ width: `${width}%`, backgroundColor: barColor }}></div>
                </div>
            </div>
        );
    };

    return (
        <div className="match-results">
            <h2>JOB MATCH ANALYSIS</h2>
            
            <div className="match-header">
                <div>
                    <h3>{job?.title || "Unknown Title"}</h3>
                    <p className="company-text">Company: <strong>{job?.company || "Unknown Company"}</strong></p>
                </div>
                
                <CircularScoreGauge 
                    targetScore={overall_score} 
                    categoryText={score_category} 
                    label="Overall Match" 
                    color={scoreColor} 
                />
            </div>

            <div className="score-breakdown">
                {renderScoreBar("Technical Skills", technical_score)}
                {renderScoreBar("Soft Skills", soft_skill_score)}
                {renderScoreBar("Experience", experience_score)}
                {renderScoreBar("Responsibilities", responsibility_score)}
                {renderScoreBar("Projects", project_score)}
                {renderScoreBar("Education", education_score)}
                {renderScoreBar("Preferred Skills", preferred_skill_score)}
                {renderScoreBar("Certifications", certification_score)}
            </div>

            <div className="match-columns">
                <div className="match-column strengths-col">
                    <h4>MATCHED SKILLS</h4>
                    {(matched_skills.length > 0 || matched_soft_skills.length > 0) ? (
                        <ul className="skill-list">
                            {matched_skills.map((s, i) => (
                                <li key={i} title={s.evidence || s.skill_name}>
                                    <span className="check">✓</span> <span className="skill-item-name">{s.skill_name}</span>
                                </li>
                            ))}
                            {matched_soft_skills.map((s, i) => (
                                <li key={`soft-${i}`} title={s.evidence || s.skill_name}>
                                    <span className="check">✓</span> <span className="skill-item-name">{s.skill_name}</span>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p className="no-data">No skills matched.</p>
                    )}
                </div>

                <div className="match-column gaps-col">
                    <h4>MISSING REQUIRED</h4>
                    {missing_required_skills.length > 0 ? (
                        <ul className="skill-list missing-required">
                            {missing_required_skills.map((s, i) => (
                                <li key={i}>
                                    <span className="add-plus red">+</span> <span className="skill-item-name">{s.skill_name}</span>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p className="no-data success-text">No required skills missing!</p>
                    )}

                    <h4 className="mt-4">MISSING PREFERRED</h4>
                    {missing_preferred_skills.length > 0 ? (
                        <ul className="skill-list missing-preferred">
                            {missing_preferred_skills.map((s, i) => (
                                <li key={i}>
                                    <span className="add-plus yellow">+</span> <span className="skill-item-name">{s.skill_name}</span>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p className="no-data">No preferred skills missing.</p>
                    )}
                </div>
            </div>

            {related_skills && related_skills.length > 0 && (
                <div className="match-section related-skills">
                    <h4>RELATED EXPERIENCE</h4>
                    <ul className="related-list">
                        {related_skills.map((s, i) => (
                            <li key={i}>
                                {s.related_skill} &rarr; related to <strong>{s.skill_name}</strong>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            <div className="match-section explanations mt-4">
                <h4>WHY THIS SCORE?</h4>
                <ul>
                    {explanations.map((exp, idx) => (
                        <li key={idx} className={exp.includes('⚠') ? 'warning' : 'success'}>
                            {exp}
                        </li>
                    ))}
                </ul>
            </div>

            <div className="disclaimer-note-card">
                <span className="note-icon">ℹ️</span>
                <span><strong>Note:</strong> This score represents Resume–Job Description semantic compatibility, not probability of getting hired.</span>
            </div>

            <div className="match-actions">
                <button className="primary-btn" onClick={onAnalyzeAnother}>
                    Analyze Another Job
                </button>
            </div>
        </div>
    );
};

export default MatchResults;
