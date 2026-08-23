import React, { useState, useEffect } from 'react';
import './ResumeVersionHistory.css';

const API_BASE_URL = 'http://127.0.0.1:5000/api';

const ResumeVersionHistory = ({ resumeId, currentJobId, onSelectVersion }) => {
    const [versions, setVersions] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchVersions = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/resume/versions/${resumeId}`);
            const data = await response.json();
            if (data.success) {
                setVersions(data.versions);
            }
        } catch (e) {
            console.error("Error loading version history");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (resumeId) {
            fetchVersions();
        }
    }, [resumeId]);

    if (loading) return <div className="vh-loading">Loading Version History...</div>;

    return (
        <div className="version-history-card">
            <h3>RESUME VERSION HISTORY ({versions.length})</h3>
            <p className="vh-subtitle">Coexisting JD-specific versions tied to your original uploaded resume.</p>
            
            <div className="versions-grid">
                {versions.length === 0 ? (
                    <div className="vh-empty">No versions generated yet. Generate your first JD-specific version below!</div>
                ) : (
                    versions.map(v => (
                        <div key={v.id} className={`vh-item ${v.status}`}>
                            <div className="vh-top">
                                <span className="vh-badge">v{v.version_number}</span>
                                <span className="vh-status">{v.status.toUpperCase()}</span>
                            </div>
                            <div className="vh-title">{v.version_name}</div>
                            
                            <div className="vh-scores">
                                {v.optimized_match_score ? (
                                    <div>Match: <strong>{v.optimized_match_score}%</strong> (ATS: {v.optimized_ats_score}%)</div>
                                ) : (
                                    <div>Base Match: <strong>{v.original_match_score || '72'}%</strong></div>
                                )}
                            </div>

                            <div className="vh-actions">
                                <button className="btn-view-v" onClick={() => onSelectVersion(v)}>
                                    {v.status === 'draft' ? 'Review Draft' : 'View Version Details'}
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default ResumeVersionHistory;
