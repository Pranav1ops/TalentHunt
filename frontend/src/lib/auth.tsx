'use client';
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi } from './api';

interface User {
    id: string;
    company_id: string;
    email: string;
    name: string;
    role: string;
    created_at: string;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (email: string, password: string) => Promise<void>;
    register: (company_name: string, name: string, email: string, password: string) => Promise<void>;
    logout: () => void;
    isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const stored = localStorage.getItem('token');
        if (stored) {
            setToken(stored);
            authApi.me()
                .then((u) => setUser(u))
                .catch(() => { localStorage.removeItem('token'); setToken(null); })
                .finally(() => setIsLoading(false));
        } else {
            setIsLoading(false);
        }
    }, []);

    const login = async (email: string, password: string) => {
        const res = await authApi.login({ email, password });
        localStorage.setItem('token', res.access_token);
        setToken(res.access_token);
        setUser(res.user);
    };

    const register = async (company_name: string, name: string, email: string, password: string) => {
        const res = await authApi.register({ company_name, name, email, password });
        localStorage.setItem('token', res.access_token);
        setToken(res.access_token);
        setUser(res.user);
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, login, register, logout, isLoading }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be inside AuthProvider');
    return ctx;
}
