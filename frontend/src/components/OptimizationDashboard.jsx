import React, { useState, useEffect } from 'react';
import ResumeVersionReview from './ResumeVersionReview';
import ResumeVersionHistory from './ResumeVersionHistory';
import './OptimizationDashboard.css';

import { API_BASE_URL } from '../services/api';

const OptimizationDashboard = ({ resumeId, jobMatchId, jobId, renderTopOnly, renderBottomOnly, onVersionFinalized }) => {
    const [optData, setOptData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [mode, setMode] = useState('balanced');
    const [editingId, setEditingId] = useState(null);
    const [editText, setEditText] = useState('');

    // Phase 10 & Gap Filter State
    const [selectedSections, setSelectedSections] = useState(() => {
        try {
            const saved = sessionStorage.getItem(`opt_sections_${resumeId}_${jobId}`);
            return saved ? JSON.parse(saved) : ['summary', 'skills', 'experience', 'projects'];
        } catch { return ['summary', 'skills', 'experience', 'projects']; }
    });

    const [confirmedSkills, setConfirmedSkills] = useState(() => {
        try {
            const saved = sessionStorage.getItem(`opt_confirmed_${resumeId}_${jobId}`);
            return saved ? JSON.parse(saved) : [];
        } catch { return []; }
    });

    const [skillAnswers, setSkillAnswers] = useState(() => {
        try {
            const saved = sessionStorage.getItem(`opt_answers_${resumeId}_${jobId}`);
            return saved ? JSON.parse(saved) : {};
        } catch { return {}; }
    });

    const [generatingVersion, setGeneratingVersion] = useState(false);
    const [activeDraftVersion, setActiveDraftVersion] = useState(null);
    const [draftChanges, setDraftChanges] = useState([]);
    const [showReviewModal, setShowReviewModal] = useState(false);
    const [activeGapFilter, setActiveGapFilter] = useState('all'); // 'all', 'high', 'moderate', 'low'

    const fetchOptimization = async (selectedMode = mode) => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE_URL}/resumes/${resumeId}/jobs/${jobId}/optimization?mode=${selectedMode}`);
            const data = await response.json();
            
            if (data.success) {
                setOptData(data);
            } else {
                setError(data.error.message);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (resumeId && jobId) {
            fetchOptimization(mode);
        }
    }, [resumeId, jobId, mode]);

    const handleAccept = async (id) => {
        try {
            const response = await fetch(`${API_BASE_URL}/optimization/suggestion/${id}/accept`, { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                setOptData(prev => {
                    const newSuggestions = prev.suggestions.map(s => s.id === id ? { ...s, status: 'accepted' } : s);
                    const newAts = { ...prev.ats };
                    if (newAts.current_score < newAts.optimized_score) {
                        newAts.current_score = Math.min(newAts.optimized_score, newAts.current_score + 3);
                        newAts.potential_improvement = newAts.optimized_score - newAts.current_score;
                    }
                    return { ...prev, suggestions: newSuggestions, ats: newAts };
                });
            }
        } catch (e) {
            console.error("Failed to accept suggestion");
        }
    };

    const handleReject = async (id) => {
        try {
            const response = await fetch(`${API_BASE_URL}/optimization/suggestion/${id}/reject`, { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                setOptData(prev => {
                    const newSuggestions = prev.suggestions.map(s => s.id === id ? { ...s, status: 'rejected' } : s);
                    return { ...prev, suggestions: newSuggestions };
                });
            }
        } catch (e) {
            console.error("Failed to reject suggestion");
        }
    };

    const handleEditSave = async (id) => {
        try {
            const response = await fetch(`${API_BASE_URL}/optimization/suggestion/${id}/edit`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ suggested_text: editText })
            });
            const data = await response.json();
            if (data.success) {
                setOptData(prev => {
                    const newSuggestions = prev.suggestions.map(s => s.id === id ? { ...s, suggested_text: editText, status: 'edited' } : s);
                    return { ...prev, suggestions: newSuggestions };
                });
                setEditingId(null);
                setEditText('');
            }
        } catch (e) {
            console.error("Failed to edit suggestion");
        }
    };

    const toggleSection = (sec) => {
        setSelectedSections(prev => {
            const next = prev.includes(sec) ? prev.filter(s => s !== sec) : [...prev, sec];
            try { sessionStorage.setItem(`opt_sections_${resumeId}_${jobId}`, JSON.stringify(next)); } catch {}
            return next;
        });
    };

    const handleSkillConfirm = (skill, answer) => {
        setSkillAnswers(prev => {
            const next = { ...prev, [skill]: answer };
            try { sessionStorage.setItem(`opt_answers_${resumeId}_${jobId}`, JSON.stringify(next)); } catch {}
            return next;
        });
        if (answer === 'yes') {
            setConfirmedSkills(prev => {
                const next = [...new Set([...prev, skill])];
                try { sessionStorage.setItem(`opt_confirmed_${resumeId}_${jobId}`, JSON.stringify(next)); } catch {}
                return next;
            });
        } else {
            setConfirmedSkills(prev => {
                const next = prev.filter(s => s !== skill);
                try { sessionStorage.setItem(`opt_confirmed_${resumeId}_${jobId}`, JSON.stringify(next)); } catch {}
                return next;
            });
        }
    };

    const handleGenerateVersion = async () => {
        setGeneratingVersion(true);
        try {
            const response = await fetch(`${API_BASE_URL}/resume/versions/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    resume_id: resumeId,
                    job_id: jobId,
                    optimization_mode: mode,
                    sections_to_optimize: selectedSections,
                    confirmed_skills: confirmedSkills
                })
            });
            const data = await response.json();
            if (data.success) {
                setActiveDraftVersion(data.version);
                setDraftChanges(data.changes);
                setShowReviewModal(true);
            }
        } catch (e) {
            console.error("Error generating draft version");
        } finally {
            setGeneratingVersion(false);
        }
    };

    const handleSelectExistingVersion = async (v) => {
        try {
            const response = await fetch(`${API_BASE_URL}/resume/versions/details/${v.id}`);
            const data = await response.json();
            if (data.success) {
                setActiveDraftVersion(data.version);
                setDraftChanges(data.changes);
                setShowReviewModal(true);
            }
        } catch (e) {
            console.error("Error fetching version details");
        }
    };

    if (loading) return <div className="opt-loading">Loading Intelligent Optimization Data...</div>;
    if (error) return <div className="opt-error">Error: {error}</div>;
    if (!optData) return null;

    const { gaps, ats, suggestions, scores } = optData;
    const allHighGaps = gaps.skill_gaps?.high_priority || [];
    const allModerateGaps = gaps.skill_gaps?.medium_priority || [];
    const allLowGaps = gaps.skill_gaps?.low_priority || [];

    const renderTop = () => (
        <>
            <div className="opt-header-row">
                <h2>RESUME OPTIMIZATION & ATS SIMULATION</h2>
            </div>
            
            {/* Score Cards Row */}
            <div className="ats-scores-row">
                <div className="ats-card match">
                    <h4>JOB MATCH SCORE</h4>
                    <div className="score-lg">{Math.round(scores?.match_score || 0)} / 100</div>
                    <div className="score-sub">Semantic Match</div>
                </div>
                <div className="ats-card current">
                    <h4>ESTIMATED ATS SCORE</h4>
                    <div className="score-lg">{Math.round(ats.current_score || 0)} / 100</div>
                    <div className="score-sub">Current Resume</div>
                </div>
                <div className="ats-card optimized">
                    <h4>ESTIMATED OPTIMIZED SCORE</h4>
                    <div className="score-lg">{Math.round(ats.optimized_score || 0)} / 100</div>
                    <div className="score-sub">After Revisions</div>
                </div>
                <div className="ats-card improvement">
                    <h4>POTENTIAL IMPROVEMENT</h4>
                    <div className="score-lg green">+{Math.round(ats.potential_improvement || 0)}</div>
                    <div className="score-sub">Points Gain</div>
                </div>
            </div>

            {/* Section ATS Completeness Scores */}
            {ats.section_scores && (
                <div className="section-scores-bar">
                    <h4>SECTION-LEVEL ATS COMPLETENESS</h4>
                    <div className="section-grid">
                        {Object.entries(ats.section_scores).map(([sec, val]) => (
                            <div key={sec} className="section-score-chip">
                                <span className="sec-name">{sec}</span>
                                <span className="sec-val">{val}%</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* PHASE 10: GENERATE JD-SPECIFIC RESUME GENERATOR CARD */}
            <div className="phase10-generator-card">
                <h3>JD-SPECIFIC RESUME GENERATOR</h3>
                <p className="gen-sub">Generate a tailored version of your resume aligned with this specific Job Description without modifying your original.</p>
                
                {/* Missing Skill Confirmation Prompts */}
                {allHighGaps.length > 0 && (
                    <div className="skill-confirm-box">
                        <div className="sc-title">⚠️ MISSING REQUIRED SKILLS CONFIRMATION</div>
                        <div className="sc-desc">The AI will NEVER inject unverified skills. Confirm if you genuinely possess any of these missing required skills:</div>
                        <div className="sc-list">
                            {allHighGaps.map(g => (
                                <div key={g.skill} className="sc-item">
                                    <span>Do you have experience with <strong>{g.skill}</strong>?</span>
                                    <div className="sc-buttons">
                                        <button className={`sc-btn ${skillAnswers[g.skill] === 'yes' ? 'yes' : ''}`} onClick={() => handleSkillConfirm(g.skill, 'yes')}>Yes, add it</button>
                                        <button className={`sc-btn ${skillAnswers[g.skill] === 'no' ? 'no' : ''}`} onClick={() => handleSkillConfirm(g.skill, 'no')}>No</button>
                                        <button className={`sc-btn ${skillAnswers[g.skill] === 'unsure' ? 'unsure' : ''}`} onClick={() => handleSkillConfirm(g.skill, 'unsure')}>Not sure</button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                <div className="gen-options-row">
                    <div className="sec-checkboxes">
                        <span>SECTIONS TO OPTIMIZE: </span>
                        {['summary', 'skills', 'experience', 'projects', 'certifications'].map(s => (
                            <label key={s} className="chk-label">
                                <input 
                                    type="checkbox" 
                                    checked={selectedSections.includes(s)}
                                    onChange={() => toggleSection(s)}
                                />
                                {s.toUpperCase()}
                            </label>
                        ))}
                    </div>

                    <button className="btn-generate-version" onClick={handleGenerateVersion} disabled={generatingVersion}>
                        {generatingVersion ? 'Generating Draft Version...' : '⚡ GENERATE JD-SPECIFIC RESUME'}
                    </button>
                </div>
            </div>
        </>
    );

    const renderBottom = () => {
        const showHigh = activeGapFilter === 'all' || activeGapFilter === 'high';
        const showModerate = activeGapFilter === 'all' || activeGapFilter === 'moderate';
        const showLow = activeGapFilter === 'all' || activeGapFilter === 'low';

        return (
            <>
                <div className="optimization-content">
                    <div className="opt-section">
                        <h3>SKILL GAP ANALYSIS</h3>

                        {/* 3 Side-by-Side Priority Selector Cards */}
                        <div className="priority-tier-cards-row">
                            <div 
                                className={`priority-tier-card high ${activeGapFilter === 'high' ? 'active' : ''}`}
                                onClick={() => setActiveGapFilter(activeGapFilter === 'high' ? 'all' : 'high')}
                            >
                                <div className="pt-header">
                                    <span className="pt-badge red">🔴 HIGH PRIORITY</span>
                                    <span className="pt-count">{allHighGaps.length}</span>
                                </div>
                                <div className="pt-desc">Missing Required Technical Skills</div>
                            </div>

                            <div 
                                className={`priority-tier-card moderate ${activeGapFilter === 'moderate' ? 'active' : ''}`}
                                onClick={() => setActiveGapFilter(activeGapFilter === 'moderate' ? 'all' : 'moderate')}
                            >
                                <div className="pt-header">
                                    <span className="pt-badge yellow">🟡 MODERATE PRIORITY</span>
                                    <span className="pt-count">{allModerateGaps.length}</span>
                                </div>
                                <div className="pt-desc">Missing Soft & Role Skills</div>
                            </div>

                            <div 
                                className={`priority-tier-card low ${activeGapFilter === 'low' ? 'active' : ''}`}
                                onClick={() => setActiveGapFilter(activeGapFilter === 'low' ? 'all' : 'low')}
                            >
                                <div className="pt-header">
                                    <span className="pt-badge teal">🔵 LOW PRIORITY</span>
                                    <span className="pt-count">{allLowGaps.length}</span>
                                </div>
                                <div className="pt-desc">Missing Preferred & Optional Skills</div>
                            </div>
                        </div>
                        
                        {/* High Priority Skill Gaps */}
                        {showHigh && allHighGaps.length > 0 && (
                            <div className="gap-category high-priority mt-3">
                                <h4>HIGH PRIORITY (Missing Required Skills)</h4>
                                <div className="gap-grid">
                                    {allHighGaps.map((g, i) => (
                                        <div key={i} className="gap-item-card high-card">
                                            <div className="gap-title">
                                                <strong>{g.skill}</strong>
                                            </div>
                                            <div className="gap-reason"><strong>Reason:</strong> {g.reason}</div>
                                            <div className="gap-action"><strong>Action:</strong> {g.action}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                        
                        {/* Moderate Priority Skill Gaps */}
                        {showModerate && allModerateGaps.length > 0 && (
                            <div className="gap-category medium-priority mt-3">
                                <h4>MODERATE PRIORITY (Missing Role & Soft Skills)</h4>
                                <div className="gap-grid">
                                    {allModerateGaps.map((g, i) => (
                                        <div key={i} className="gap-item-card moderate-card">
                                            <div className="gap-title">
                                                <strong>{g.skill}</strong>
                                            </div>
                                            <div className="gap-reason"><strong>Reason:</strong> {g.reason}</div>
                                            {g.action && <div className="gap-action"><strong>Action:</strong> {g.action}</div>}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Low Priority Skill Gaps */}
                        {showLow && allLowGaps.length > 0 && (
                            <div className="gap-category low-priority mt-3">
                                <h4>LOW PRIORITY (Missing Preferred & Optional Skills)</h4>
                                <div className="gap-grid">
                                    {allLowGaps.map((g, i) => (
                                        <div key={i} className="gap-item-card low-card">
                                            <div className="gap-title">
                                                <strong>{g.skill}</strong>
                                            </div>
                                            <div className="gap-reason"><strong>Reason:</strong> {g.reason}</div>
                                            {g.action && <div className="gap-action"><strong>Action:</strong> {g.action}</div>}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                        
                        {gaps.learning_roadmap && gaps.learning_roadmap.length > 0 && (
                            <div className="roadmap-section mt-4">
                                <h4>SUGGESTED LEARNING ROADMAP</h4>
                                <ul>
                                    {gaps.learning_roadmap.map((step, i) => <li key={i}>{step}</li>)}
                                </ul>
                            </div>
                        )}
                    </div>

                    <div className="opt-section mt-4">
                        <h3>ACTIONABLE IMPROVEMENTS</h3>
                        <div className="suggestions-list">
                            {suggestions.length === 0 ? (
                                <p>No major structural improvements needed!</p>
                            ) : (
                                suggestions.map((s, i) => {
                                    const statusVal = s.status || 'pending';
                                    return (
                                        <div key={s.id || `sugg-${i}`} className={`suggestion-card ${statusVal}`}>
                                            <div className="sugg-header">
                                                <span className="sugg-section">{(s.section || 'General').toUpperCase()}</span>
                                                <span className={`sugg-impact ${(s.impact || 'medium').toLowerCase()}`}>{s.impact || 'Medium'} Impact</span>
                                            </div>
                                            <div className="sugg-reason">{s.reason}</div>
                                            
                                            <div className="before-after">
                                                <div className="before">
                                                    <strong>Current:</strong> "{s.original_text}"
                                                </div>
                                                <div className="after">
                                                    <strong>Recommended:</strong> 
                                                    {editingId === s.id && s.id ? (
                                                        <div className="edit-box">
                                                            <textarea 
                                                                value={editText} 
                                                                onChange={e => setEditText(e.target.value)}
                                                                rows={3}
                                                            />
                                                            <div className="edit-actions">
                                                                <button className="btn-save" onClick={() => handleEditSave(s.id)}>Save & Apply</button>
                                                                <button className="btn-cancel" onClick={() => setEditingId(null)}>Cancel</button>
                                                            </div>
                                                        </div>
                                                    ) : (
                                                        <span> "{s.suggested_text}"</span>
                                                    )}
                                                </div>
                                            </div>
                                            
                                            {statusVal === 'pending' && editingId !== s.id ? (
                                                <div className="sugg-actions">
                                                    {s.id && <button className="btn-accept" onClick={() => handleAccept(s.id)}>Accept</button>}
                                                    {s.id && <button className="btn-edit" onClick={() => { setEditingId(s.id); setEditText(s.suggested_text); }}>Edit</button>}
                                                    {s.id && <button className="btn-reject" onClick={() => handleReject(s.id)}>Reject</button>}
                                                </div>
                                            ) : statusVal !== 'pending' ? (
                                                <div className="sugg-status">✓ Status: {statusVal.toUpperCase()} (Resume Version updated)</div>
                                            ) : null}
                                        </div>
                                    );
                                })
                            )}
                        </div>
                    </div>

                    {/* Resume Version History Component */}
                    <ResumeVersionHistory 
                        resumeId={resumeId} 
                        currentJobId={jobId} 
                        onSelectVersion={handleSelectExistingVersion}
                    />
                </div>

                {/* Review Draft Modal */}
                {showReviewModal && activeDraftVersion && (
                    <ResumeVersionReview 
                        version={activeDraftVersion}
                        changes={draftChanges}
                        onClose={() => setShowReviewModal(false)}
                        onFinalized={() => {
                            fetchOptimization(mode);
                        }}
                    />
                )}
            </>
        );
    };

    return (
        <div className="optimization-dashboard">
            {renderTopOnly ? renderTop() : renderBottomOnly ? renderBottom() : (
                <>
                    {renderTop()}
                    {renderBottom()}
                </>
            )}

            {/* Review Draft Modal — Always rendered if active */}
            {showReviewModal && activeDraftVersion && (
                <ResumeVersionReview 
                    version={activeDraftVersion}
                    changes={draftChanges}
                    onClose={() => setShowReviewModal(false)}
                    onFinalized={(finalVersion, parsedData) => {
                        fetchOptimization(mode);
                        setShowReviewModal(false);
                        if (onVersionFinalized) onVersionFinalized(finalVersion, parsedData);
                    }}
                />
            )}
        </div>
    );
};

export default OptimizationDashboard;
