import React, { useState } from 'react';
import UploadBox from './UploadBox';
import './LandingPage.css';

const LandingPage = ({ onUploadSuccess, onOpenAuthModal, user, isAuthenticated, logout }) => {
  const [beforeAfterToggle, setBeforeAfterToggle] = useState('after');

  const scrollToUpload = () => {
    const el = document.getElementById('upload-section');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  const scrollToSection = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="landing-page">
      {/* SECTION 1 — STICKY NAVIGATION */}
      <nav className="landing-nav">
        <div className="landing-container landing-nav-inner">
          <div className="nav-brand" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
            <div className="nav-logo-icon">📄</div>
            <span className="nav-logo-text">ResumeIQ</span>
          </div>

          <ul className="nav-links">
            <li><a href="#features" onClick={(e) => { e.preventDefault(); scrollToSection('features'); }}>Features</a></li>
            <li><a href="#how-it-works" onClick={(e) => { e.preventDefault(); scrollToSection('how-it-works'); }}>How It Works</a></li>
            <li><a href="#why-resumeiq" onClick={(e) => { e.preventDefault(); scrollToSection('why-resumeiq'); }}>Why ResumeIQ</a></li>
          </ul>

          <div className="nav-auth">
            {isAuthenticated ? (
              <div className="user-profile-badge">
                <div className="user-avatar-circle">
                  {(user?.name || user?.email || 'U')[0].toUpperCase()}
                </div>
                <span className="user-welcome">
                  Welcome, <strong>{user?.name || user?.email?.split('@')[0]}</strong>
                </span>
                <button className="btn-auth-action signout" onClick={logout}>Sign Out</button>
              </div>
            ) : (
              <>
                <button className="btn-nav-signin" onClick={() => onOpenAuthModal('signin')}>Sign In</button>
                <button className="btn-nav-signup" onClick={() => onOpenAuthModal('signup')}>Create Account</button>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* SECTION 3 — HERO SECTION */}
      <section className="hero-section">
        <div className="landing-container">
          <h1 className="hero-title">
            Build a Resume That <span className="highlight">Matches the Job.</span>
          </h1>

          <p className="hero-subtitle">
            Analyze your resume, discover skill gaps, improve ATS compatibility, and create job-specific resume versions with ResumeIQ.
          </p>

          <div className="hero-cta-group">
            <button className="btn-primary-cta" onClick={scrollToUpload}>
              Analyze My Resume
            </button>
            <button className="btn-secondary-cta" onClick={() => scrollToSection('how-it-works')}>
              See How It Works
            </button>
          </div>

          {/* SECTION 4 — RESUME UPLOAD CONTAINER */}
          <div className="hero-upload-wrapper" id="upload-section">
            <UploadBox onUploadSuccess={onUploadSuccess} />
          </div>
        </div>
      </section>

      {/* SECTION 5 — PRODUCT FEATURES */}
      <section className="features-section" id="features">
        <div className="landing-container">
          <div className="section-header">
            <span className="section-tag">Powerful AI Features</span>
            <h2 className="section-title">Everything You Need to Build a Stronger Resume</h2>
            <p className="section-subtitle">
              From your first upload to your final application, ResumeIQ helps you understand, improve, and tailor your resume.
            </p>
          </div>

          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon-wrapper">📄</div>
              <h3>Resume Analysis</h3>
              <p>Understand your resume's strengths, weaknesses, structure, and overall quality with deep section parsing.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon-wrapper">🎯</div>
              <h3>ATS Optimization</h3>
              <p>Improve ATS compatibility and identify hidden layout or keyword formatting issues that reduce visibility.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon-wrapper">🔍</div>
              <h3>Job Matching</h3>
              <p>See how closely your resume matches specific job descriptions with explainable 5-layer score breakdowns.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon-wrapper">🧩</div>
              <h3>Skill Gap Analysis</h3>
              <p>Discover the technical & soft skills you already have and the critical missing keywords required by employers.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon-wrapper">✨</div>
              <h3>AI Recommendations</h3>
              <p>Get actionable, job-specific suggestions and line-by-line bullet rewrites to maximize impact.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon-wrapper">📊</div>
              <h3>Version Tracking</h3>
              <p>Create, compare, edit, and manage tailored versions of your resume for every target application.</p>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 6 — HOW IT WORKS */}
      <section className="how-it-works-section" id="how-it-works">
        <div className="landing-container">
          <div className="section-header">
            <span className="section-tag">Simple 4-Step Process</span>
            <h2 className="section-title">How ResumeIQ Works</h2>
            <p className="section-subtitle">
              Turn your existing resume into a job-ready application in four simple steps.
            </p>
          </div>

          <div className="steps-grid">
            <div className="step-card">
              <span className="step-number">01</span>
              <h3>UPLOAD</h3>
              <p>Upload your resume in PDF or DOCX format for instant structure parsing.</p>
            </div>

            <div className="step-card">
              <span className="step-number">02</span>
              <h3>ANALYZE</h3>
              <p>Understand your resume's strengths, weaknesses, and ATS parser readability score.</p>
            </div>

            <div className="step-card">
              <span className="step-number">03</span>
              <h3>MATCH</h3>
              <p>Paste a job description to calculate exact skill alignment and keyword coverage.</p>
            </div>

            <div className="step-card">
              <span className="step-number">04</span>
              <h3>OPTIMIZE</h3>
              <p>Apply AI-powered recommendations, edit live, and export a polished PDF or DOCX.</p>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 7 — PRODUCT PREVIEW MOCKUP */}
      <section className="product-preview-section">
        <div className="landing-container">
          <div className="section-header">
            <span className="section-tag">Employer Perspective</span>
            <h2 className="section-title">See Your Resume Through the Eyes of an Employer</h2>
            <p className="section-subtitle">
              Get an instant preview of how applicant tracking systems and hiring managers evaluate your profile.
            </p>
          </div>

          <div className="preview-mockup-card">
            <div className="mockup-header-bar">
              <div className="mockup-dots">
                <div className="mockup-dot red"></div>
                <div className="mockup-dot yellow"></div>
                <div className="mockup-dot green"></div>
              </div>
              <span className="mockup-title-text">ResumeIQ Dashboard — Sample Candidate Analysis</span>
            </div>

            <div className="mockup-body">
              <div className="preview-scores-row">
                <div className="preview-score-box">
                  <span>ATS Readability</span>
                  <div className="preview-score-num blue">86%</div>
                </div>
                <div className="preview-score-box">
                  <span>Job Match Score</span>
                  <div className="preview-score-num green">84%</div>
                </div>
                <div className="preview-score-box">
                  <span>Skill Coverage</span>
                  <div className="preview-score-num blue">88%</div>
                </div>
                <div className="preview-score-box">
                  <span>Potential Gain</span>
                  <div className="preview-score-num green">+24 pts</div>
                </div>
              </div>

              <div className="preview-bars-group">
                <div className="preview-bar-item">
                  <span className="preview-bar-label">Technical Skills Match</span>
                  <div className="preview-bar-track">
                    <div className="preview-bar-fill" style={{ width: '88%' }}></div>
                  </div>
                  <span className="preview-bar-val">88%</span>
                </div>
                <div className="preview-bar-item">
                  <span className="preview-bar-label">Keyword Alignment</span>
                  <div className="preview-bar-track">
                    <div className="preview-bar-fill" style={{ width: '82%' }}></div>
                  </div>
                  <span className="preview-bar-val">82%</span>
                </div>
                <div className="preview-bar-item">
                  <span className="preview-bar-label">Formatting & Structure</span>
                  <div className="preview-bar-track">
                    <div className="preview-bar-fill" style={{ width: '92%' }}></div>
                  </div>
                  <span className="preview-bar-val">92%</span>
                </div>
              </div>

              <div className="preview-highlights">
                <span className="ph-chip success">✓ Strong Core Engineering Skills</span>
                <span className="ph-chip warning">⚠ Missing: Docker, Cloud Deployments</span>
                <span className="ph-chip info">✦ Active Verb Bullet Suggestions Available</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 8 — BEFORE / AFTER COMPARISON */}
      <section className="before-after-section">
        <div className="landing-container">
          <div className="section-header">
            <span className="section-tag">Proven Optimization</span>
            <h2 className="section-title">See the Difference</h2>
            <p className="section-subtitle">
              Turn a generic resume into a job-specific resume tailored for your target opportunity.
            </p>
          </div>

          <div className="ba-card-grid">
            <div className="ba-card before">
              <div className="ba-header">
                <span className="ba-tag">BEFORE OPTIMIZATION</span>
                <div className="ba-score">61%</div>
              </div>
              <ul className="ba-list">
                <li>❌ Generic summary statement</li>
                <li>❌ Weak passive action verbs ("Responsible for...")</li>
                <li>❌ Missing target job keywords & tools</li>
                <li>❌ Unstructured skills section</li>
              </ul>
            </div>

            <div className="ba-card after">
              <div className="ba-header">
                <span className="ba-tag">AFTER RESUMEIQ</span>
                <div className="ba-score">86%</div>
              </div>
              <ul className="ba-list">
                <li>✓ Role-aligned professional summary</li>
                <li>✓ High-impact metric bullet points ("Architected...")</li>
                <li>✓ Prioritized technical keywords matching JD</li>
                <li>✓ Clean, 100% ATS-readable template</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 9 — WHY RESUMEIQ */}
      <section className="why-section" id="why-resumeiq">
        <div className="landing-container">
          <div className="section-header">
            <span className="section-tag">Core Advantage</span>
            <h2 className="section-title">More Than Just an ATS Checker</h2>
            <p className="section-subtitle">
              ResumeIQ goes beyond static keyword counting to give you a complete career intelligence toolkit.
            </p>
          </div>

          <div className="why-grid">
            <div className="why-card">
              <h3>🎯 JOB-SPECIFIC</h3>
              <p>Optimize your resume specifically for the exact role and employer you are applying for.</p>
            </div>

            <div className="why-card">
              <h3>🧠 AI-POWERED</h3>
              <p>Get intelligent, context-aware bullet rewrites and skill gap recommendations based on real job requirements.</p>
            </div>

            <div className="why-card">
              <h3>📈 DATA-DRIVEN</h3>
              <p>Understand your ATS score, job match %, skill coverage, and improvement areas with explainable scoring.</p>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 10 & 11 — FINAL CTA */}
      <section className="final-cta-section">
        <div className="landing-container final-cta-content">
          <h2>Ready to Build a Better Resume?</h2>
          <p>Find out what your resume is missing and make it job-ready in minutes.</p>
          <button className="btn-primary-cta" onClick={scrollToUpload}>
            Analyze My Resume
          </button>
        </div>
      </section>

      {/* SECTION 12 — FOOTER */}
      <footer className="landing-footer">
        <div className="landing-container">
          <div className="footer-grid">
            <div className="footer-brand">
              <h2>ResumeIQ</h2>
              <p>Build a Resume That Matches the Job. AI-powered resume analysis, ATS optimization, and job matching platform.</p>
            </div>

            <div className="footer-col">
              <h4>PRODUCT</h4>
              <ul>
                <li><a href="#features" onClick={(e) => { e.preventDefault(); scrollToSection('features'); }}>Resume Analysis</a></li>
                <li><a href="#features" onClick={(e) => { e.preventDefault(); scrollToSection('features'); }}>ATS Optimization</a></li>
                <li><a href="#features" onClick={(e) => { e.preventDefault(); scrollToSection('features'); }}>Job Matching</a></li>
                <li><a href="#features" onClick={(e) => { e.preventDefault(); scrollToSection('features'); }}>Skill Gap Analysis</a></li>
              </ul>
            </div>

            <div className="footer-col">
              <h4>RESOURCES</h4>
              <ul>
                <li><a href="#how-it-works" onClick={(e) => { e.preventDefault(); scrollToSection('how-it-works'); }}>How It Works</a></li>
                <li><a href="#why-resumeiq" onClick={(e) => { e.preventDefault(); scrollToSection('why-resumeiq'); }}>Why ResumeIQ</a></li>
              </ul>
            </div>

            <div className="footer-col">
              <h4>ACCOUNT</h4>
              <ul>
                <li><a href="#signin" onClick={(e) => { e.preventDefault(); onOpenAuthModal('signin'); }}>Sign In</a></li>
                <li><a href="#signup" onClick={(e) => { e.preventDefault(); onOpenAuthModal('signup'); }}>Create Account</a></li>
              </ul>
            </div>
          </div>

          <div className="footer-bottom">
            © 2026 ResumeIQ. All rights reserved. Built for modern job seekers.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
