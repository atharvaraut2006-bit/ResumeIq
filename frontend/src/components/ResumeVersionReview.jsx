import React, { useState } from 'react';
import './ResumeVersionReview.css';

const API_BASE_URL = 'http://127.0.0.1:5000/api';

const ResumeVersionReview = ({ version, changes: initialChanges, onFinalized, onClose }) => {
    const [changes, setChanges] = useState(initialChanges || []);
    const [editingId, setEditingId] = useState(null);
    const [editText, setEditText] = useState('');
    const [finalizing, setFinalizing] = useState(false);
    const [rescoreResult, setRescoreResult] = useState(null);

    const handleAccept = async (id) => {
        try {
            const response = await fetch(`${API_BASE_URL}/resume/changes/${id}/accept`, { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                setChanges(prev => prev.map(c => c.id === id ? { ...c, status: 'accepted' } : c));
            }
        } catch (e) {
            console.error("Error accepting change");
        }
    };

    const handleReject = async (id) => {
        try {
            const response = await fetch(`${API_BASE_URL}/resume/changes/${id}/reject`, { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                setChanges(prev => prev.map(c => c.id === id ? { ...c, status: 'rejected' } : c));
            }
        } catch (e) {
            console.error("Error rejecting change");
        }
    };

    const handleEditSave = async (id) => {
        try {
            const response = await fetch(`${API_BASE_URL}/resume/changes/${id}/edit`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ new_text: editText })
            });
            const data = await response.json();
            if (data.success) {
                setChanges(prev => prev.map(c => c.id === id ? { ...c, new_text: editText, status: data.change.status } : c));
                setEditingId(null);
            }
        } catch (e) {
            console.error("Error editing change");
        }
    };

    const handleFinalize = async () => {
        setFinalizing(true);
        try {
            const response = await fetch(`${API_BASE_URL}/resume/versions/${version.id}/finalize`, { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                setRescoreResult(data.rescore);
                if (onFinalized) onFinalized(data.version, data.parsed_data);
            }
        } catch (e) {
            console.error("Error finalizing version");
        } finally {
            setFinalizing(false);
        }
    };

    return (
        <div className="version-review-modal">
            <div className="version-review-card">
                <div className="review-header">
                    <div>
                        <h2>OPTIMIZED RESUME DRAFT REVIEW</h2>
                        <div className="v-name">{version.version_name} (Version {version.version_number})</div>
                    </div>
                    <button className="btn-close" onClick={onClose}>✕ Close</button>
                </div>

                {rescoreResult && (
                    <div className="rescore-banner">
                        <div className="rescore-title">🎉 RESCORE SUCCESSFUL!</div>
                        <div className="rescore-metrics">
                            <div>
                                <span>Match Score:</span> <strong>{rescoreResult.original_match_score}% ➔ {rescoreResult.optimized_match_score}%</strong>
                                <span className="badge-gain">+{rescoreResult.match_improvement}%</span>
                            </div>
                            <div>
                                <span>ATS Score:</span> <strong>{rescoreResult.original_ats_score}% ➔ {rescoreResult.optimized_ats_score}%</strong>
                                <span className="badge-gain">+{rescoreResult.ats_improvement}%</span>
                            </div>
                        </div>
                    </div>
                )}

                <div className="changes-list">
                    <h3>SECTION REWRITES & REORGANIZATION ({changes.length})</h3>
                    
                    {changes.length === 0 ? (
                        <p>No explicit section changes proposed.</p>
                    ) : (
                        changes.map(c => (
                            <div key={c.id} className={`change-card ${c.status}`}>
                                <div className="c-header">
                                    <span className="c-section">{c.section.toUpperCase()}</span>
                                    <span className={`c-impact ${c.impact.toLowerCase()}`}>{c.impact} Impact</span>
                                </div>
                                <div className="c-reason"><strong>Why:</strong> {c.reason}</div>

                                <div className="side-by-side">
                                    <div className="col-orig">
                                        <div className="col-label">ORIGINAL SOURCE</div>
                                        <div className="text-box">{c.original_text || '(Empty section)'}</div>
                                    </div>
                                    <div className="col-new">
                                        <div className="col-label">OPTIMIZED PROPOSAL</div>
                                        {editingId === c.id ? (
                                            <div className="edit-box">
                                                <textarea 
                                                    value={editText} 
                                                    onChange={e => setEditText(e.target.value)}
                                                    rows={4}
                                                />
                                                <div className="edit-actions">
                                                    <button className="btn-save" onClick={() => handleEditSave(c.id)}>Save</button>
                                                    <button className="btn-cancel" onClick={() => setEditingId(null)}>Cancel</button>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="text-box highlight">{c.new_text}</div>
                                        )}
                                    </div>
                                </div>

                                {c.status === 'pending' && editingId !== c.id ? (
                                    <div className="c-actions">
                                        <button className="btn-accept" onClick={() => handleAccept(c.id)}>Accept</button>
                                        <button className="btn-edit" onClick={() => { setEditingId(c.id); setEditText(c.new_text); }}>Edit</button>
                                        <button className="btn-reject" onClick={() => handleReject(c.id)}>Reject</button>
                                    </div>
                                ) : (
                                    <div className="c-status">Status: <strong>{c.status.toUpperCase()}</strong></div>
                                )}
                            </div>
                        ))
                    )}
                </div>

                <div className="review-footer">
                    {!rescoreResult ? (
                        <button className="btn-finalize" onClick={handleFinalize} disabled={finalizing}>
                            {finalizing ? 'Finalizing & Re-scoring...' : 'Finalize & Save Optimized Version'}
                        </button>
                    ) : (
                        <button className="btn-finalize done" onClick={onClose}>Done (Version Saved)</button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ResumeVersionReview;
