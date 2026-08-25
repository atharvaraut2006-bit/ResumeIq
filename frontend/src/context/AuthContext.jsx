import React, { createContext, useContext, useState, useEffect } from 'react';

import { API_BASE_URL } from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(() => localStorage.getItem('resumeiq_token'));
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const verifyAuth = async () => {
            if (!token) {
                setIsLoading(false);
                return;
            }

            try {
                const response = await fetch(`${API_BASE_URL}/auth/me`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                const data = await response.json();
                if (data.success && data.user) {
                    setUser(data.user);
                } else {
                    // Token invalid or expired
                    logout();
                }
            } catch (err) {
                console.error("Auth verification failed", err);
            } finally {
                setIsLoading(false);
            }
        };

        verifyAuth();
    }, [token]);

    const login = async (email, password) => {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();
        
        if (data.success && data.token) {
            localStorage.setItem('resumeiq_token', data.token);
            setToken(data.token);
            setUser(data.user);
            return { success: true, user: data.user };
        } else {
            return { success: false, message: data.error?.message || 'Failed to sign in.' };
        }
    };

    const signup = async (name, email, password) => {
        const response = await fetch(`${API_BASE_URL}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
        const data = await response.json();

        if (data.success && data.token) {
            localStorage.setItem('resumeiq_token', data.token);
            setToken(data.token);
            setUser(data.user);
            return { success: true, user: data.user };
        } else {
            return { success: false, message: data.error?.message || 'Failed to create account.' };
        }
    };

    const logout = () => {
        localStorage.removeItem('resumeiq_token');
        setToken(null);
        setUser(null);
    };

    const convertGuestData = async (resumeId) => {
        if (!token || !resumeId) return;
        try {
            await fetch(`${API_BASE_URL}/auth/convert-guest`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ resume_id: resumeId })
            });
        } catch (e) {
            console.error("Failed to convert guest data", e);
        }
    };

    return (
        <AuthContext.Provider value={{
            user,
            token,
            isAuthenticated: !!user,
            isLoading,
            login,
            signup,
            logout,
            convertGuestData
        }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
