import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import './ImprovementCoach.css';

import { API_BASE_URL } from '../services/api';

const ImprovementCoach = ({ 
    resumeId, 
    jobId, 
    resumeData, 
    onUpdateResumeData, 
    onNavigateToExport,
    planData: parentPlanData,
    setPlanData: setParentPlanData,
    acceptedRecs: parentAcceptedRecs,
    setAcceptedRecs: setParentAcceptedRecs
}) => {
    const { token } = useAuth();
    
    // Internal fallback states if parent props not provided
    const [localPlanData, setLocalPlanData] = useState(null);
    const [localAcceptedRecs, setLocalAcceptedRecs] = useState([]);

    const planData = parentPlanData !== undefined ? parentPlanData : localPlanData;
    const setPlanData = setParentPlanData || setLocalPlanData;

    const acceptedRecs = parentAcceptedRecs !== undefined ? parentAcceptedRecs : localAcceptedRecs;
    const setAcceptedRecs = setParentAcceptedRecs || setLocalAcceptedRecs;

    const [loading, setLoading] = useState(!planData);
    const [error, setError] = useState(null);
    const [filterCategory, setFilterCategory] = useState('all'); // 'all', 'quick', 'deep'
    const [applyingId, setApplyingId] = useState(null);

    useEffect(() => {
        if (resumeId && jobId && !planData) {
            fetchImprovementPlan();
        } else if (planData) {
            setLoading(false);
        }
    }, [resumeId, jobId, planData]);

    const fetchImprovementPlan = async () => {
        setLoading(true);
        setError(null);
        try {
            const headers = {};
            if (token) headers['Authorization'] = `Bearer ${token}`;

            const res = await fetch(`${API_BASE_URL}/resumes/${resumeId}/jobs/${jobId}/improvement-plan`, { headers });
            const data = await res.json();

            if (data.success) {
                setPlanData(data);
            } else {
                setError(data.error?.message || "Failed to load resume strategy.");
            }
        } catch (e) {
            setError("Connection error while loading resume strategy.");
        } finally {
            setLoading(false);
        }
    };

    const handleAcceptRecommendation = (rec) => {
        setApplyingId(rec.id);
        
        // Update plan state
        if (planData && planData.recommendations) {
            const updatedRecs = planData.recommendations.map(r => 
                r.id === rec.id ? { ...r, status: 'accepted' } : r
            );
            setPlanData({
                ...planData,
                recommendations: updatedRecs
            });
        }

        setAcceptedRecs(prev => {
            const list = Array.isArray(prev) ? prev : [];
            if (list.some(r => r.id === rec.id)) return list;
            return [...list, rec];
        });

        setTimeout(() => setApplyingId(null), 300);
    };

    const handleRejectRecommendation = (recId) => {
        if (planData && planData.recommendations) {
            const updatedRecs = planData.recommendations.map(r => 
                r.id === recId ? { ...r, status: 'rejected' } : r
            );
            setPlanData({
                ...planData,
                recommendations: updatedRecs
            });
        }
        setAcceptedRecs(prev => (Array.isArray(prev) ? prev.filter(r => r.id !== recId) : []));
    };

    const handleApplyAllAndRedirect = () => {
        if (!resumeData || !onUpdateResumeData) {
            if (onNavigateToExport) onNavigateToExport();
            return;
        }

        const currentSkills = Array.isArray(resumeData.skills) ? [...resumeData.skills] : [];
        let rawSkillsText = resumeData.skills_raw || "";
        let newSummary = resumeData.summary || "";
        let currentProjects = Array.isArray(resumeData.projects) ? resumeData.projects.map(p => ({ ...p })) : [];
        let currentExperience = Array.isArray(resumeData.experience) ? resumeData.experience.map(e => ({ ...e })) : [];
        let newRawText = resumeData.raw_text || "";

        (acceptedRecs || []).forEach(rec => {
            const titleLower = (rec.title || '').toLowerCase();
            const catLower = (rec.category || '').toLowerCase();

            // 1. Missing Keyword Recommendation
            if (catLower === 'missing_keywords' || titleLower.includes('missing keyword') || titleLower.includes('add keyword')) {
                const kwMatch = rec.title ? rec.title.match(/['"]([^'"]+)['"]/) : null;
                if (kwMatch && kwMatch[1]) {
                    const kw = kwMatch[1].trim();
                    if (!currentSkills.includes(kw)) {
                        currentSkills.push(kw);
                    }
                    if (!rawSkillsText.toLowerCase().includes(kw.toLowerCase())) {
                        rawSkillsText += (rawSkillsText ? ", " : "") + kw;
                    }
                }
            } 
            // 2. Summary Improvement Recommendation
            else if (catLower === 'summary' || titleLower.includes('summary')) {
                if (rec.after_text) {
                    newSummary = rec.after_text;
                    if (rec.before_text && newRawText.includes(rec.before_text)) {
                        newRawText = newRawText.replace(rec.before_text, rec.after_text);
                    }
                }
            } 
            // 3. Project Improvement / Quantification Recommendation
            else if (catLower === 'projects' || catLower === 'quantification' || titleLower.includes('project')) {
                if (rec.before_text && rec.after_text) {
                    let replacedInProj = false;
                    currentProjects = currentProjects.map(p => {
                        const raw = p.raw || p.description || "";
                        if (raw.includes(rec.before_text)) {
                            replacedInProj = true;
                            return { ...p, raw: raw.replace(rec.before_text, rec.after_text), description: (p.description || "").replace(rec.before_text, rec.after_text) };
                        }
                        return p;
                    });
                    if (!replacedInProj && currentProjects.length > 0) {
                        const firstProj = currentProjects[0];
                        const oldRaw = firstProj.raw || firstProj.description || "";
                        currentProjects[0] = {
                            ...firstProj,
                            raw: oldRaw ? oldRaw + "\n• " + rec.after_text : rec.after_text,
                            description: rec.after_text
                        };
                    }
                    if (newRawText.includes(rec.before_text)) {
                        newRawText = newRawText.replace(rec.before_text, rec.after_text);
                    }
                }
            }
            // 4. Experience Improvement Recommendation
            else if (catLower === 'experience' || titleLower.includes('experience') || titleLower.includes('role')) {
                if (rec.before_text && rec.after_text) {
                    currentExperience = currentExperience.map(e => {
                        const raw = e.raw || e.description || "";
                        if (raw.includes(rec.before_text)) {
                            return { ...e, raw: raw.replace(rec.before_text, rec.after_text), description: (e.description || "").replace(rec.before_text, rec.after_text) };
                        }
                        return e;
                    });
                    if (newRawText.includes(rec.before_text)) {
                        newRawText = newRawText.replace(rec.before_text, rec.after_text);
                    }
                }
            }
            // Fallback for general skills/text rewrites
            else if (rec.after_text) {
                const cleanAfter = rec.after_text.replace(/^[•\-\*\s]+/, '').trim();
                if (cleanAfter.includes(':')) {
                    rawSkillsText += "\n" + cleanAfter;
                }
            }
        });

        const updatedResume = {
            ...resumeData,
            skills: currentSkills,
            skills_raw: rawSkillsText,
            summary: newSummary,
            projects: currentProjects,
            experience: currentExperience,
            raw_text: newRawText,
            is_edited: true
        };

        onUpdateResumeData(updatedResume);

        if (onNavigateToExport) {
            onNavigateToExport();
        }
    };

    if (loading) {
        return (
            <div className="coach-loading-card">
                <div className="spinner"></div>
                <p>Analyzing resume & job requirements for actionable strategy...</p>
            </div>
        );
    }

    if (error) {
        return <div className="coach-error-card">⚠️ {error}</div>;
    }

    const { career_readiness, strengths, recommendations, learning_suggestions } = planData || {};

    const filteredRecommendations = (recommendations || []).filter(r => {
        if (filterCategory === 'quick') return ['missing_keywords', 'summary', 'ats'].includes(r.category);
        if (filterCategory === 'deep') return ['experience', 'projects', 'quantification'].includes(r.category);
        return true;
    });

    return (
        <div className="improvement-coach-container">
            {/* Header & Overview */}
            <div className="coach-header-bar">
                <h2>🎯 RESUME STRATEGY & KEYWORD OPTIMIZER</h2>
                <p>Actionable keyword additions, section enhancements, and phrase optimizations tailored for ATS compliance.</p>
            </div>

            {/* Career Readiness Score Summary - All Blue Cards */}
            {career_readiness && (
                <div className="career-readiness-grid">
                    <div className="readiness-card">
                        <span className="readiness-label">Overall Readiness</span>
                        <span className="readiness-val">{career_readiness.overall_score}%</span>
                        <span className="readiness-sub">Composite Index</span>
                    </div>

                    <div className="readiness-card">
                        <span className="readiness-label">Resume Quality</span>
                        <span className="readiness-val">{career_readiness.resume_quality}%</span>
                        <span className="readiness-sub">Structure & Content</span>
                    </div>

                    <div className="readiness-card">
                        <span className="readiness-label">ATS Readiness</span>
                        <span className="readiness-val">{career_readiness.ats_readiness}%</span>
                        <span className="readiness-sub">Parser Compliance</span>
                    </div>

                    <div className="readiness-card">
                        <span className="readiness-label">JD Skill Coverage</span>
                        <span className="readiness-val">{career_readiness.skill_coverage}%</span>
                        <span className="readiness-sub">Target Match</span>
                    </div>
                </div>
            )}

            {/* Top Strengths Section - Distinct Green Accent Panel */}
            {strengths && strengths.length > 0 && (
                <div className="strengths-card-panel">
                    <h3>🌟 TOP RESUME STRENGTHS</h3>
                    <div className="strengths-list">
                        {strengths.map((s, idx) => (
                            <div key={idx} className="strength-item">
                                <strong>✓ {s.title}:</strong> {s.detail}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Batch Apply Sticky Action Banner */}
            {acceptedRecs && acceptedRecs.length > 0 && (
                <div className="batch-apply-bar">
                    <div className="batch-info">
                        <span className="batch-count">✨ {acceptedRecs.length} Improvement(s) Selected</span>
                        <span>Click to apply all selected changes to your resume and open Live Builder.</span>
                    </div>
                    <button className="btn-batch-apply-redirect" onClick={handleApplyAllAndRedirect}>
                        Apply Selected Improvements & Open Builder →
                    </button>
                </div>
            )}

            {/* Prioritized Improvement Plan Section */}
            <div className="roadmap-section">
                <div className="roadmap-header">
                    <h3>📋 PRIORITIZED RESUME IMPROVEMENT PLAN</h3>
                    
                    <div className="filter-tab-group">
                        <button 
                            className={`filter-btn ${filterCategory === 'all' ? 'active' : ''}`}
                            onClick={() => setFilterCategory('all')}
                        >
                            All ({recommendations ? recommendations.length : 0})
                        </button>
                        <button 
                            className={`filter-btn ${filterCategory === 'quick' ? 'active' : ''}`}
                            onClick={() => setFilterCategory('quick')}
                        >
                            ⚡ Quick Fixes
                        </button>
                        <button 
                            className={`filter-btn ${filterCategory === 'deep' ? 'active' : ''}`}
                            onClick={() => setFilterCategory('deep')}
                        >
                            🎯 Deep Improvements
                        </button>
                    </div>
                </div>

                <div className="recommendations-list">
                    {filteredRecommendations.map(rec => (
                        <div key={rec.id} className={`rec-card priority-${(rec.priority || 'medium').toLowerCase()} status-${rec.status || 'pending'}`}>
                            <div className="rec-card-header">
                                <div className="rec-badge-group">
                                    <span className={`priority-pill ${(rec.priority || 'medium').toLowerCase()}`}>{rec.priority || 'MEDIUM'}</span>
                                </div>
                                {rec.status === 'accepted' && <span className="status-tag accepted">✓ ACCEPTED</span>}
                                {rec.status === 'rejected' && <span className="status-tag rejected">✕ DISMISSED</span>}
                            </div>

                            <h4 className="rec-title">{rec.title}</h4>
                            <p className="rec-desc">{rec.description}</p>

                            {/* Clean Current Text vs Proposed Improvement Diff View */}
                            {rec.before_text && rec.after_text && (
                                <div className="diff-view-box">
                                    <div className="diff-col before">
                                        <span className="diff-label">CURRENT TEXT:</span>
                                        <code>{rec.before_text}</code>
                                    </div>
                                    <div className="diff-col after">
                                        <span className="diff-label">PROPOSED IMPROVEMENT:</span>
                                        <code>{rec.after_text}</code>
                                    </div>
                                </div>
                            )}

                            {/* Action Buttons - Always rendered when not accepted or rejected */}
                            {rec.status !== 'accepted' && rec.status !== 'rejected' && (
                                <div className="rec-actions-bar">
                                    <button 
                                        className="btn-apply-rec" 
                                        onClick={() => handleAcceptRecommendation(rec)}
                                        disabled={applyingId === rec.id}
                                    >
                                        Accept & Apply Improvement
                                    </button>
                                    <button 
                                        className="btn-reject-rec" 
                                        onClick={() => handleRejectRecommendation(rec.id)}
                                    >
                                        Dismiss
                                    </button>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Target Skill Learning Suggestions */}
            {learning_suggestions && learning_suggestions.length > 0 && (
                <div className="learning-suggestions-panel">
                    <h3>💡 SKILL ROADMAP & TARGET ROLE RECOMMENDATIONS</h3>
                    <p className="sub-text">Technologies frequently requested across job descriptions in your domain:</p>
                    <div className="learning-grid">
                        {learning_suggestions.map((ls, i) => (
                            <div key={i} className="learning-card">
                                <strong>{ls.technology}</strong>
                                <span>{ls.reason}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default ImprovementCoach;
