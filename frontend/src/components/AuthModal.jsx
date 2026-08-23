import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import './AuthModal.css';

const AuthModal = ({ isOpen, initialMode = 'signin', onClose, currentResumeId }) => {
    const { login, signup, convertGuestData } = useAuth();
    const [mode, setMode] = useState(initialMode); // 'signin' or 'signup'
    
    // Form fields
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');

    // UI States
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const emailInputRef = useRef(null);

    useEffect(() => {
        setMode(initialMode);
        setError(null);
    }, [initialMode, isOpen]);

    useEffect(() => {
        if (isOpen && emailInputRef.current) {
            setTimeout(() => emailInputRef.current?.focus(), 150);
        }
    }, [isOpen, mode]);

    if (!isOpen) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);

        if (mode === 'signup') {
            if (!name.trim()) {
                setError('Please enter your full name.');
                return;
            }
            if (password !== confirmPassword) {
                setError('Passwords do not match.');
                return;
            }
            if (password.length < 6) {
                setError('Password must be at least 6 characters.');
                return;
            }
        }

        setLoading(true);

        try {
            let res;
            if (mode === 'signin') {
                res = await login(email, password);
            } else {
                res = await signup(name, email, password);
            }

            if (res.success) {
                if (currentResumeId) {
                    await convertGuestData(currentResumeId);
                }
                onClose();
            } else {
                setError(res.message);
            }
        } catch (err) {
            setError(err.message || 'An unexpected error occurred.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-modal-backdrop" onClick={onClose}>
            <div className="auth-modal-card" onClick={e => e.stopPropagation()}>
                <button className="auth-close-btn" onClick={onClose}>✕</button>

                <div className="auth-header">
                    <h2>{mode === 'signin' ? 'Welcome Back' : 'Create Account'}</h2>
                    <p>{mode === 'signin' ? 'Sign in to access your resumes, versions, and analyses.' : 'Start building job-specific, ATS-optimized resumes.'}</p>
                </div>

                <div className="auth-tabs">
                    <button 
                        type="button"
                        className={`auth-tab-btn ${mode === 'signin' ? 'active' : ''}`}
                        onClick={() => { setMode('signin'); setError(null); }}
                    >
                        Sign In
                    </button>
                    <button 
                        type="button"
                        className={`auth-tab-btn ${mode === 'signup' ? 'active' : ''}`}
                        onClick={() => { setMode('signup'); setError(null); }}
                    >
                        Create Account
                    </button>
                </div>

                {error && <div className="auth-error-alert">⚠️ {error}</div>}

                <form onSubmit={handleSubmit} className="auth-form">
                    {mode === 'signup' && (
                        <div className="form-group">
                            <label>Full Name</label>
                            <input 
                                type="text" 
                                placeholder="Atharva Raut"
                                value={name}
                                onChange={e => setName(e.target.value)}
                                required
                            />
                        </div>
                    )}

                    <div className="form-group">
                        <label>Email Address</label>
                        <input 
                            ref={emailInputRef}
                            type="email" 
                            placeholder="atharva@example.com"
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Password</label>
                        <input 
                            type="password" 
                            placeholder="••••••••"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    {mode === 'signup' && (
                        <div className="form-group">
                            <label>Confirm Password</label>
                            <input 
                                type="password" 
                                placeholder="••••••••"
                                value={confirmPassword}
                                onChange={e => setConfirmPassword(e.target.value)}
                                required
                            />
                        </div>
                    )}

                    {currentResumeId && mode === 'signup' && (
                        <div className="guest-transfer-notice">
                            💡 <strong>Save Resume:</strong> Your current uploaded resume will automatically be saved to your new account.
                        </div>
                    )}

                    <button type="submit" className="btn-auth-submit" disabled={loading}>
                        {loading ? (mode === 'signin' ? 'Signing in...' : 'Creating account...') : (mode === 'signin' ? 'Sign In' : 'Create Account')}
                    </button>
                </form>

                <div className="auth-footer-toggle">
                    {mode === 'signin' ? (
                        <span>Don't have an account? <button type="button" onClick={() => setMode('signup')}>Create an account</button></span>
                    ) : (
                        <span>Already have an account? <button type="button" onClick={() => setMode('signin')}>Sign In</button></span>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AuthModal;
