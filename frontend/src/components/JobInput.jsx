import React, { useState } from 'react';
import { createJob, analyzeJob, matchResumeToJob } from '../services/api';
import './JobInput.css';

const JobInput = ({ resumeId, onMatchSuccess }) => {
    const [description, setDescription] = useState('');
    const [title, setTitle] = useState('');
    const [company, setCompany] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleAnalyze = async () => {
        if (!description.trim() || description.length < 100) {
            setError('Please enter a valid, longer job description (at least 100 characters).');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            // 1. Create Job
            const jobResult = await createJob({
                title,
                company,
                description
            });

            const jobId = jobResult.job.id;

            // 2. Analyze Job Requirements (Phase 4)
            await analyzeJob(jobId);
            
            // 3. Match Resume to Job (Phase 5 & 6)
            const matchResult = await matchResumeToJob(resumeId, jobId);
            
            onMatchSuccess(matchResult);
            
        } catch (err) {
            setError(err.error?.message || 'An error occurred while analyzing the job.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="job-input-container">
            <h3>Job Description</h3>
            <p>Paste the job description below:</p>
            
            <div className="form-group">
                <input 
                    type="text" 
                    placeholder="Job Title (Optional)" 
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                />
                <input 
                    type="text" 
                    placeholder="Company (Optional)" 
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                />
            </div>

            <textarea
                placeholder="Paste full job description here..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows="10"
            ></textarea>
            
            {error && <div className="error-message">{error}</div>}
            
            <button 
                onClick={handleAnalyze} 
                disabled={loading}
                className="analyze-btn"
            >
                {loading ? 'Analyzing Job...' : 'Analyze Job'}
            </button>
        </div>
    );
};

export default JobInput;
