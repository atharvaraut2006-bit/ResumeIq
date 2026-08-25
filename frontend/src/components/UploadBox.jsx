import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { uploadResume, parseResume, extractSkills } from '../services/api';
import './UploadBox.css';

const UploadBox = ({ onUploadSuccess }) => {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [statusStep, setStatusStep] = useState('');
    const [error, setError] = useState(null);
    const [validationFailed, setValidationFailed] = useState(false);
    const [successMessage, setSuccessMessage] = useState(null);
    const [validationInfo, setValidationInfo] = useState(null);

    const onDrop = useCallback(acceptedFiles => {
        const selected = acceptedFiles[0];
        if (selected) {
            const ext = selected.name.split('.').pop().toLowerCase();
            if (!['pdf', 'docx'].includes(ext)) {
                setError('Invalid file format. Supported formats: PDF, DOCX.');
                setValidationFailed(true);
                setFile(null);
                return;
            }
            if (selected.size > 5 * 1024 * 1024) {
                setError('File size exceeds maximum allowed limit of 5MB.');
                setValidationFailed(true);
                setFile(null);
                return;
            }
            setFile(selected);
            setError(null);
            setValidationFailed(false);
            setSuccessMessage(null);
            setValidationInfo(null);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
        onDrop,
        accept: {'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']},
        multiple: false
    });

    const handleUpload = async () => {
        if (!file || validationFailed) return;
        
        setUploading(true);
        setError(null);
        setSuccessMessage(null);
        setValidationFailed(false);
        
        try {
            // Progressive status step 1
            setStatusStep('Checking your file format and readability...');
            const uploadResult = await uploadResume(file);
            
            // Progressive status step 2
            setStatusStep('Verifying document content structure...');
            const resumeId = uploadResult.resume.id;
            setValidationInfo(uploadResult.validation);

            // Progressive status step 3
            setStatusStep('Reading resume sections and skills...');
            const parseResult = await parseResume(resumeId);
            const skillsResult = await extractSkills(resumeId);
            
            setSuccessMessage(`✓ Resume verified successfully (${Math.round((uploadResult.validation?.confidence || 0.95) * 100)}% Confidence)`);
            onUploadSuccess(resumeId, parseResult.parsed_resume, skillsResult.skills, uploadResult.resume.original_filename);
            
        } catch (err) {
            setValidationFailed(true);
            const msg = err.message || err.error?.message || 'An error occurred during resume processing. Please try again.';
            setError(msg);
        } finally {
            setUploading(false);
            setStatusStep('');
        }
    };

    const handleResetUpload = () => {
        setFile(null);
        setError(null);
        setValidationFailed(false);
        setSuccessMessage(null);
        setValidationInfo(null);
    };

    return (
        <div className="upload-container">
            <div className="upload-header">
                <h2>Upload Your Resume</h2>
                <p>Drop your resume here to get started. Supports PDF and DOCX</p>
            </div>
            
            {!validationFailed && (
                <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
                    <input {...getInputProps()} />
                    <div className="dropzone-icon">📄</div>
                    {isDragActive ? (
                        <p className="dropzone-text primary">Drop your resume file here...</p>
                    ) : (
                        <>
                            <p className="dropzone-text primary">Drag & drop your resume here, or click to browse</p>
                            <span className="btn-browse-file">Choose File</span>
                            <span className="format-info-badge">Supports PDF & DOCX • Max 5MB</span>
                        </>
                    )}
                </div>
            )}
            
            {file && !validationFailed && (
                <div className="selected-file">
                    <p className="file-info-text">Selected file: <strong>{file.name}</strong> ({(file.size / (1024 * 1024)).toFixed(2)} MB)</p>
                    {uploading && <div className="validation-progress">⏳ {statusStep}</div>}
                    
                    <button 
                        onClick={handleUpload} 
                        disabled={uploading}
                        className="upload-btn"
                    >
                        {uploading ? 'Validating & Analyzing...' : 'Analyze Resume'}
                    </button>
                </div>
            )}

            {/* Validation / Connection Error Display */}
            {validationFailed && (
                <div className="validation-error-card">
                    <div className="ve-icon">⚠️</div>
                    <h3>{error?.toLowerCase().includes('server') || error?.toLowerCase().includes('network') || error?.toLowerCase().includes('connection') ? 'SERVER CONNECTION ISSUE' : 'DOCUMENT VALIDATION FAILED'}</h3>
                    <p className="ve-msg">{error}</p>
                    
                    <button className="btn-reupload" onClick={file ? handleUpload : handleResetUpload}>
                        🔄 {file ? 'Retry Upload' : 'Try Uploading Another File'}
                    </button>
                </div>
            )}

            {validationInfo?.is_resume && (
                <div className="validation-success-chip">
                    ✓ Resume detected (Confidence: {Math.round(validationInfo.confidence * 100)}%)
                </div>
            )}
            
            {successMessage && <div className="success-message">{successMessage}</div>}
        </div>
    );
};

export default UploadBox;
