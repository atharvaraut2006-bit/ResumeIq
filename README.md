# 📄 ResumeIQ — Resume Analyzer & Job Matching Platform

ResumeIQ is a full-stack, enterprise-grade Resume Analysis, Job Matching, ATS Optimization, and Resume Builder platform. It transforms raw candidate resumes into job-specific, ATS-optimized, downloadable PDF and DOCX documents with explainable scoring and 1-click strategy optimization.

---

## 🌟 Key Features (Phases 0 – 15)

- **📄 2-Level Resume Validation & Parsing (Phases 1–3):** Machine-readable text extraction from PDF/DOCX with 2-level content verification rejecting non-resume files.
- **🎯 Job Description & Multi-JD Analysis (Phases 5–6):** Extracts required technical skills, soft skills, responsibilities, and experience metrics from employer JDs.
- **🔍 Explainable Resume–JD Matching (Phase 7):** Semantic vector embeddings (`sentence-transformers/all-MiniLM-L6-v2`) calculating factual overall, technical, experience, and education match scores.
- **📊 Priority Skill Gap Analysis (Phase 8):** Side-by-side priority cards (Red for High, Yellow for Moderate, Teal for Low priority skill gaps).
- **⚡ Mode-Dependent ATS Simulator (Phase 9):** Conservative, Balanced, and Aggressive ATS scoring modes calculating exact parser readability.
- **📝 AI Rewriting & Resume Versioning (Phase 10):** Fact-validated AI bullet rewrites creating versioned resume branches (`v1`, `v2`).
- **🎨 Professional Resume Builder & Export Engine (Phases 11–12):** 4 ATS-friendly templates (ATS Focused, Classic Professional, Modern Minimal, Technical) with live paper preview, dynamic section reordering, and direct PDF/DOCX downloads.
- **🔒 Authentication & User Account System (Auth Phase):** Password hashing (`werkzeug.security`), JWT token authentication, guest-to-account data conversion, and strict IDOR user data isolation.
- **🤖 Personalized Improvement Plan & Career Strategy (Phase 13):** AI Coach with Career Readiness metrics, Top Strengths, 1-Click Before/After Apply diffs, and live re-analysis score gains.
- **🛡️ Security, Performance & Monitoring (Phases 14–15):** Rate limiting, strict input validation, zero hallucination guardrails, and production deployment configuration.

---

## 🏗️ Architecture & Tech Stack

- **Frontend:** React 18, Vite, CSS Modules, Context API (`AuthContext`), SVG Animated Gauge Circles.
- **Backend:** Python 3.12, Flask, SQLAlchemy, SQLite, ReportLab (PDF Engine), `python-docx` (DOCX Engine), PyJWT.
- **AI & Semantic Engine:** HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (Runs 100% locally with zero paid third-party API dependencies).

---

## 🚀 Quick Start & Local Setup

### 1. Clone Repository & Environment
```bash
git clone https://github.com/atharvaraut2006-bit/resume_analyzer.git
cd resume_analyzer
cp .env.example .env
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate      # Windows
# source venv/bin/activate   # Linux/macOS

pip install -r requirements.txt
python run.py
```
Backend will start at `http://127.0.0.1:5000`.

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend will start at `http://127.0.0.1:5173`.

---

## 📑 API Overview

- `POST /api/auth/signup` — Create user account with hashed password.
- `POST /api/auth/login` — Sign in and issue JWT token.
- `GET /api/auth/me` — Verify authenticated user profile.
- `POST /api/resumes/upload` — Upload PDF/DOCX resume with 2-level validation.
- `POST /api/resumes/<id>/parse` — Extract structured JSON sections.
- `POST /api/jobs` — Create & parse Job Description.
- `POST /api/jobs/<id>/match/<resume_id>` — Generate explainable match scores.
- `GET /api/resume/templates` — Fetch available export templates.
- `POST /api/resume/versions/<id>/export` — Generate downloadable PDF or DOCX file.
- `GET /api/resumes/<id>/jobs/<id>/improvement-plan` — Generate prioritized coaching plan.
- `POST /api/recommendations/<id>/accept` — Apply recommendation, create new version, and re-analyze scores.

---

## 🔒 Security & Data Privacy

- **Password Hashing:** Passwords hashed using PBKDF2/scrypt salts via `werkzeug.security`.
- **IDOR Protection:** All resource access endpoints verify `resource.user_id == current_user.id`.
- **Fact Safety:** Zero hallucination guardrails—never fabricates unverified skills, experience, or certifications.

---

## 📜 License
Developed for educational and professional career development. All rights reserved.
