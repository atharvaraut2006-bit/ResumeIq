import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import './ImprovementCoach.css';

const API_BASE_URL = 'http://127.0.0.1:5000/api';

const ImprovementCoach = ({ resumeId, jobId }) => {
    const { token } = useAuth();
    const [planData, setPlanData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filterCategory, setFilterCategory] = useState('all'); // 'all', 'quick', 'deep'
    const [scoreGainToast, setScoreGainToast] = useState(null);
    const [applyingId, setApplyingId] = useState(null);

    useEffect(() => {
        if (resumeId && jobId) {
            fetchImprovementPlan();
        }
    }, [resumeId, jobId]);

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
                setError(data.error?.message || "Failed to load AI improvement coach.");
            }
        } catch (e) {
            setError("Connection error while loading AI coach.");
        } finally {
            setLoading(false);
        }
    };

    const handleAcceptRecommendation = async (recId) => {
        setApplyingId(recId);
        try {
            const headers = { 'Content-Type': 'application/json' };
            if (token) headers['Authorization'] = `Bearer ${token}`;

            const res = await fetch(`${API_BASE_URL}/recommendations/${recId}/accept`, {
                method: 'POST',
                headers
            });
            const data = await res.json();

            if (data.success) {
                setScoreGainToast(data.score_gain);
                // Update local status
                setPlanData(prev => ({
                    ...prev,
                    recommendations: prev.recommendations.map(r => 
                        r.id === recId ? { ...r, status: 'accepted' } : r
                    )
                }));
                setTimeout(() => setScoreGainToast(null), 6000);
            }
        } catch (e) {
            console.error("Failed to apply recommendation", e);
        } finally {
            setApplyingId(null);
        }
    };

    const handleRejectRecommendation = async (recId) => {
        try {
            const headers = { 'Content-Type': 'application/json' };
            if (token) headers['Authorization'] = `Bearer ${token}`;

            await fetch(`${API_BASE_URL}/recommendations/${recId}/reject`, {
                method: 'POST',
                headers
            });

            setPlanData(prev => ({
                ...prev,
                recommendations: prev.recommendations.map(r => 
                    r.id === recId ? { ...r, status: 'rejected' } : r
                )
            }));
        } catch (e) {
            console.error("Failed to reject recommendation", e);
        }
    };

    const handleFeedback = async (recId, useful) => {
        try {
            const headers = { 'Content-Type': 'application/json' };
            if (token) headers['Authorization'] = `Bearer ${token}`;

            await fetch(`${API_BASE_URL}/recommendations/${recId}/feedback`, {
                method: 'POST',
                headers,
                body: JSON.stringify({ useful })
            });

            setPlanData(prev => ({
                ...prev,
                recommendations: prev.recommendations.map(r => 
                    r.id === recId ? { ...r, feedback: useful } : r
                )
            }));
        } catch (e) {
            console.error("Failed to submit feedback", e);
        }
    };

    if (loading) {
        return (
            <div className="coach-loading-card">
                <div className="spinner"></div>
                <p>AI Resume Coach is analyzing your resume & job requirements...</p>
            </div>
        );
    }

    if (error) {
        return <div className="coach-error-card">⚠️ {error}</div>;
    }

    const { career_readiness, strengths, recommendations, learning_suggestions } = planData;

    const filteredRecommendations = recommendations.filter(r => {
        if (filterCategory === 'quick') return ['missing_keywords', 'summary', 'ats'].includes(r.category);
        if (filterCategory === 'deep') return ['experience', 'projects', 'quantification'].includes(r.category);
        return true;
    });

    return (
        <div className="improvement-coach-container">
            {/* Score Gain Alert Toast */}
            {scoreGainToast && (
                <div className="score-gain-toast">
                    🚀 <strong>Recommendation Applied!</strong> Smart Re-Analysis Complete:
                    <span className="gain-pill">ATS Score: {scoreGainToast.old_ats} → {scoreGainToast.new_ats} (+{scoreGainToast.ats_diff} pts)</span>
                    <span className="gain-pill">JD Match: {scoreGainToast.old_match} → {scoreGainToast.new_match} (+{scoreGainToast.match_diff} pts)</span>
                </div>
            )}

            {/* Header & Overview */}
            <div className="coach-header-bar">
                <h2>🎯 PERSONALIZED IMPROVEMENT PLAN & CAREER STRATEGY</h2>
                <p>Prioritized, explainable improvements based on your resume and job description analysis.</p>
            </div>

            {/* Career Readiness Score Summary */}
            <div className="career-readiness-grid">
                <div className="readiness-card primary">
                    <span className="readiness-label">Overall Readiness</span>
                    <span className="readiness-val">{career_readiness.overall_score}%</span>
                    <span className="readiness-sub">Composite Career Index</span>
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

            {/* Top Strengths Section */}
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

            {/* Prioritized Improvement Plan Section */}
            <div className="roadmap-section">
                <div className="roadmap-header">
                    <h3>📋 PRIORITIZED RESUME IMPROVEMENT PLAN</h3>
                    
                    <div className="filter-tab-group">
                        <button 
                            className={`filter-btn ${filterCategory === 'all' ? 'active' : ''}`}
                            onClick={() => setFilterCategory('all')}
                        >
                            All ({recommendations.length})
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
                        <div key={rec.id} className={`rec-card priority-${rec.priority.toLowerCase()} status-${rec.status}`}>
                            <div className="rec-card-header">
                                <div className="rec-badge-group">
                                    <span className={`priority-pill ${rec.priority.toLowerCase()}`}>{rec.priority}</span>
                                    <span className="confidence-pill">{rec.confidence}% Confidence</span>
                                </div>
                                {rec.status === 'accepted' && <span className="status-tag accepted">✓ APPLIED</span>}
                                {rec.status === 'rejected' && <span className="status-tag rejected">✕ DISMISSED</span>}
                            </div>

                            <h4 className="rec-title">{rec.title}</h4>
                            <p className="rec-desc">{rec.description}</p>
                            
                            <div className="rec-reason-box">
                                💡 <strong>Why this matters:</strong> {rec.reason}
                            </div>

                            {/* Before vs After Diff View */}
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

                            {/* Impact Badge */}
                            {rec.impact && (
                                <div className="rec-impact">
                                    📈 <strong>Expected Impact:</strong> {rec.impact}
                                </div>
                            )}

                            {/* Action Buttons */}
                            {rec.status === 'pending' && (
                                <div className="rec-actions-bar">
                                    <button 
                                        className="btn-apply-rec" 
                                        onClick={() => handleAcceptRecommendation(rec.id)}
                                        disabled={applyingId === rec.id}
                                    >
                                        {applyingId === rec.id ? 'Applying & Re-analyzing...' : '⚡ Accept & Apply Improvement'}
                                    </button>
                                    <button 
                                        className="btn-reject-rec" 
                                        onClick={() => handleRejectRecommendation(rec.id)}
                                    >
                                        Dismiss
                                    </button>
                                </div>
                            )}

                            {/* Feedback Mechanism */}
                            <div className="rec-feedback-footer">
                                <span>Was this recommendation helpful?</span>
                                <button 
                                    className={`btn-fb ${rec.feedback === true ? 'active' : ''}`}
                                    onClick={() => handleFeedback(rec.id, true)}
                                >
                                    👍 Yes
                                </button>
                                <button 
                                    className={`btn-fb ${rec.feedback === false ? 'active' : ''}`}
                                    onClick={() => handleFeedback(rec.id, false)}
                                >
                                    👎 No
                                </button>
                            </div>
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
