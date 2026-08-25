import React, { useState, useEffect } from 'react';
import LandingPage from './components/LandingPage';
import UploadBox from './components/UploadBox';
import ResumePreview from './components/ResumePreview';
import JobInput from './components/JobInput';
import MatchResults from './components/MatchResults';
import OptimizationDashboard from './components/OptimizationDashboard';
import ResumeBuilderExport from './components/ResumeBuilderExport';
import ImprovementCoach from './components/ImprovementCoach';
import { checkHealth } from './services/api';
import './App.css';

import { useAuth } from './context/AuthContext';
import AuthModal from './components/AuthModal';

function App() {
  const { user, isAuthenticated, logout } = useAuth();
  const [backendStatus, setBackendStatus] = useState('checking');
  const [resumeData, setResumeData] = useState(null);
  const [resumeSkills, setResumeSkills] = useState(null);
  const [filename, setFilename] = useState('');
  const [matchData, setMatchData] = useState(null);
  const [activeTab, setActiveTab] = useState('match');

  // Auth Modal State
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authModalMode, setAuthModalMode] = useState('signin');

  useEffect(() => {
    const verifyHealth = async () => {
      try {
        await checkHealth();
        setBackendStatus('connected');
      } catch (error) {
        setBackendStatus('disconnected');
      }
    };
    verifyHealth();
  }, []);

  const handleUploadSuccess = (resumeId, data, skills, name) => {
    setResumeData({ ...data, id: resumeId });
    setResumeSkills(skills);
    setFilename(name);
  };

  const handleMatchSuccess = (matchResult) => {
    setMatchData(matchResult);
    setActiveTab('match');
  };

  const handleAnalyzeAnother = () => {
    setMatchData(null);
  };

  const resetAll = () => {
    setResumeData(null);
    setResumeSkills(null);
    setFilename('');
    setMatchData(null);
  };

  const handleVersionFinalized = (finalVersion, parsedData) => {
    if (parsedData) {
      setResumeData(prev => ({ ...prev, ...parsedData }));
    } else if (finalVersion && finalVersion.parsed_data) {
      try {
        const parsed = JSON.parse(finalVersion.parsed_data);
        setResumeData(prev => ({ ...prev, ...parsed }));
      } catch (e) {}
    }
    setActiveTab('export');
  };

  const handleUpdateResumeData = (updatedData) => {
    setResumeData(updatedData);
  };

  const openAuthModal = (mode = 'signin') => {
    setAuthModalMode(mode);
    setIsAuthModalOpen(true);
  };

  if (!resumeData) {
    return (
      <div className="app-landing-wrapper">
        <AuthModal 
          isOpen={isAuthModalOpen} 
          onClose={() => setIsAuthModalOpen(false)} 
          initialMode={authModalMode} 
        />
        <LandingPage 
          onUploadSuccess={handleUploadSuccess}
          onOpenAuthModal={openAuthModal}
          user={user}
          isAuthenticated={isAuthenticated}
          logout={logout}
        />
      </div>
    );
  }

  return (
    <div className="app-container">
      {/* Auth Modal Dialog */}
      <AuthModal 
        isOpen={isAuthModalOpen} 
        onClose={() => setIsAuthModalOpen(false)} 
        initialMode={authModalMode} 
        currentResumeId={resumeData?.id}
      />

      <header className="app-header">
        <div className="header-top-row">
          <div className="brand">
            <h1>📄 ResumeIQ</h1>
            <span className="subtitle">A Smarter Way to Build Your Career.</span>
          </div>

          <div className="auth-header-controls">
            {isAuthenticated ? (
              <div className="user-profile-badge">
                <div className="user-avatar-circle">
                  {(user?.name || user?.email || 'U')[0].toUpperCase()}
                </div>
                <span className="user-welcome">
                  Welcome, <strong>{user?.name || user?.email?.split('@')[0]}</strong>
                </span>
                <button className="btn-auth-action signout" onClick={logout}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                  Sign Out
                </button>
              </div>
            ) : (
              <div className="auth-action-buttons">
                <button className="btn-auth-action signin" onClick={() => { setAuthModalMode('signin'); setIsAuthModalOpen(true); }}>
                  Sign In
                </button>
                <button className="btn-auth-action signup" onClick={() => { setAuthModalMode('signup'); setIsAuthModalOpen(true); }}>
                  Create Account
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="app-main">
        {!resumeData ? (
          <UploadBox onUploadSuccess={handleUploadSuccess} />
        ) : (
          <div className="workspace">
            {/* Centered Green Success Banner */}
            <div className="success-banner">
              Resume uploaded successfully ({filename || 'Uploaded'}).
            </div>

            {matchData && (
              <div className="workspace-tabs">
                <button 
                  className={`tab-btn ${activeTab === 'match' ? 'active' : ''}`}
                  onClick={() => setActiveTab('match')}
                >
                  Job Match Analysis
                </button>
                <button 
                  className={`tab-btn ${activeTab === 'optimize' ? 'active' : ''}`}
                  onClick={() => setActiveTab('optimize')}
                >
                  ATS Optimization & Skill Gaps
                </button>
                <button 
                  className={`tab-btn ${activeTab === 'export' ? 'active' : ''}`}
                  onClick={() => setActiveTab('export')}
                >
                  Resume Builder & Export
                </button>
                <button 
                  className={`tab-btn ${activeTab === 'coach' ? 'active' : ''}`}
                  onClick={() => setActiveTab('coach')}
                >
                  Career Strategy & Roadmap
                </button>
              </div>
            )}

            {(!matchData || activeTab === 'match') ? (
              <div className="split-view">
                <div className="resume-col">
                  <ResumePreview data={resumeData} skills={resumeSkills} filename={filename} onReset={resetAll} />
                </div>

                <div className="job-col">
                  {!matchData ? (
                    <JobInput resumeId={resumeData.id} onMatchSuccess={handleMatchSuccess} />
                  ) : (
                    <MatchResults matchData={matchData} onAnalyzeAnother={handleAnalyzeAnother} />
                  )}
                </div>
              </div>
            ) : activeTab === 'optimize' ? (
              /* Phase 8/9/10 Optimization & Skill Gap 50:50 View */
              <div className="split-view">
                <div className="resume-col">
                  <OptimizationDashboard 
                    resumeId={resumeData.id} 
                    jobId={matchData.job_id || matchData.job?.id} 
                    jobMatchId={matchData.job_match_id} 
                    renderSkillGapsOnly={true}
                    onVersionFinalized={handleVersionFinalized}
                  />
                </div>

                <div className="job-col">
                  <OptimizationDashboard 
                    resumeId={resumeData.id} 
                    jobId={matchData.job_id || matchData.job?.id} 
                    jobMatchId={matchData.job_match_id} 
                    renderAtsOptimizationOnly={true}
                    onVersionFinalized={handleVersionFinalized}
                  />
                </div>
              </div>
            ) : activeTab === 'export' ? (
              /* Phase 11 & 12 Resume Builder & Export Engine View */
              <ResumeBuilderExport 
                resumeId={resumeData.id}
                jobId={matchData.job_id || matchData.job?.id}
                resumeData={resumeData}
                onUpdateResumeData={handleUpdateResumeData}
              />
            ) : (
              /* Phase 13 AI Resume Coach & Personalized Career Roadmap View */
              <ImprovementCoach 
                resumeId={resumeData.id}
                jobId={matchData.job_id || matchData.job?.id}
              />
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
