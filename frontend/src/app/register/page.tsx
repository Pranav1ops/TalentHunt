'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import Link from 'next/link';

export default function RegisterPage() {
    const [form, setForm] = useState({ company_name: '', name: '', email: '', password: '' });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { register } = useAuth();
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await register(form.company_name, form.name, form.email, form.password);
            router.push('/dashboard');
        } catch (err: any) {
            setError(err.message || 'Registration failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center px-4">
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -right-40 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl" />
                <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-accent-500/10 rounded-full blur-3xl" />
            </div>

            <div className="w-full max-w-md relative animate-fade-in">
                <div className="text-center mb-8">
                    <div className="inline-flex items-center gap-3 mb-4">
                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center shadow-lg shadow-primary-500/30">
                            <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                        </div>
                        <span className="text-2xl font-bold bg-gradient-to-r from-primary-300 to-purple-300 bg-clip-text text-transparent">
                            TalentHunt
                        </span>
                    </div>
                    <p className="text-dark-400 text-sm">Create your recruiter account</p>
                </div>

                <div className="glass-card p-8">
                    <h2 className="text-xl font-semibold text-dark-100 mb-6">Get Started</h2>

                    {error && (
                        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-300 text-sm">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-dark-300 mb-2">Company Name</label>
                            <input
                                id="register-company"
                                type="text"
                                value={form.company_name}
                                onChange={(e) => setForm({ ...form, company_name: e.target.value })}
                                className="input-field"
                                placeholder="Your Company"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-dark-300 mb-2">Your Name</label>
                            <input
                                id="register-name"
                                type="text"
                                value={form.name}
                                onChange={(e) => setForm({ ...form, name: e.target.value })}
                                className="input-field"
                                placeholder="John Doe"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-dark-300 mb-2">Email</label>
                            <input
                                id="register-email"
                                type="email"
                                value={form.email}
                                onChange={(e) => setForm({ ...form, email: e.target.value })}
                                className="input-field"
                                placeholder="you@company.com"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-dark-300 mb-2">Password</label>
                            <input
                                id="register-password"
                                type="password"
                                value={form.password}
                                onChange={(e) => setForm({ ...form, password: e.target.value })}
                                className="input-field"
                                placeholder="Minimum 8 characters"
                                required
                                minLength={8}
                            />
                        </div>
                        <button
                            id="register-submit"
                            type="submit"
                            disabled={loading}
                            className="btn-primary w-full flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                'Create Account'
                            )}
                        </button>
                    </form>

                    <div className="mt-6 text-center text-sm text-dark-400">
                        Already have an account?{' '}
                        <Link href="/login" className="text-primary-400 hover:text-primary-300 font-medium">
                            Sign in
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
