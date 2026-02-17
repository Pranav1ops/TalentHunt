'use client';
import { useState, useEffect } from 'react';
import { analyticsApi } from '@/lib/api';
import Link from 'next/link';

export default function DashboardPage() {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        analyticsApi.overview()
            .then(setData)
            .catch(() => setData(null))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <DashboardSkeleton />;

    const stats = [
        { label: 'Total Candidates', value: data?.total_candidates || 0, icon: '👥', gradient: 'from-blue-500 to-cyan-500', href: '/dashboard/candidates' },
        { label: 'Job Descriptions', value: data?.total_jobs || 0, icon: '📋', gradient: 'from-purple-500 to-pink-500', href: '/dashboard/jobs' },
        { label: 'AI Matches', value: data?.total_matches || 0, icon: '🎯', gradient: 'from-amber-500 to-orange-500', href: '/dashboard/jobs' },
        { label: 'Rediscovery Signals', value: data?.rediscovery_signals_count || 0, icon: '✨', gradient: 'from-emerald-500 to-teal-500', href: '/dashboard/analytics' },
    ];

    return (
        <div className="animate-fade-in">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-dark-100 mb-2">Dashboard</h1>
                <p className="text-dark-400">Rediscover hidden talent in your candidate database</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
                {stats.map((stat) => (
                    <Link key={stat.label} href={stat.href} className="glass-card-hover p-5 group">
                        <div className="flex items-center justify-between mb-4">
                            <span className="text-2xl">{stat.icon}</span>
                            <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${stat.gradient} opacity-20 group-hover:opacity-30 transition-opacity`} />
                        </div>
                        <div className="text-3xl font-bold text-dark-100 mb-1">{stat.value}</div>
                        <div className="text-sm text-dark-400">{stat.label}</div>
                    </Link>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Avg Match Score */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold text-dark-200 mb-4">Match Quality</h3>
                    <div className="flex items-center gap-6">
                        <div className="relative w-28 h-28">
                            <svg className="w-28 h-28 -rotate-90" viewBox="0 0 100 100">
                                <circle cx="50" cy="50" r="40" fill="none" stroke="#1e293b" strokeWidth="8" />
                                <circle
                                    cx="50" cy="50" r="40" fill="none" stroke="url(#scoreGradient)" strokeWidth="8"
                                    strokeLinecap="round" strokeDasharray={`${(data?.avg_match_score || 0) * 2.51} 251`}
                                />
                                <defs>
                                    <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                        <stop offset="0%" stopColor="#6366f1" />
                                        <stop offset="100%" stopColor="#a855f7" />
                                    </linearGradient>
                                </defs>
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center">
                                <span className="text-2xl font-bold text-dark-100">{data?.avg_match_score || 0}</span>
                            </div>
                        </div>
                        <div>
                            <div className="text-sm text-dark-400 mb-2">Average Match Score</div>
                            <div className="text-xs text-dark-500">Across all computed matches</div>
                        </div>
                    </div>
                </div>

                {/* Top Skills */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold text-dark-200 mb-4">Top Skills in Database</h3>
                    <div className="space-y-3">
                        {(data?.top_skills || []).slice(0, 6).map((s: any, i: number) => (
                            <div key={i} className="flex items-center gap-3">
                                <span className="text-sm text-dark-300 w-24 truncate">{s.skill}</span>
                                <div className="flex-1 score-bar">
                                    <div
                                        className="score-fill bg-gradient-to-r from-primary-500 to-purple-500"
                                        style={{ width: `${Math.min(100, (s.count / (data?.total_candidates || 1)) * 100)}%` }}
                                    />
                                </div>
                                <span className="text-xs text-dark-500 w-8 text-right">{s.count}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="mt-8 glass-card p-6">
                <h3 className="text-lg font-semibold text-dark-200 mb-4">Quick Actions</h3>
                <div className="flex flex-wrap gap-3">
                    <Link href="/dashboard/jobs" className="btn-primary text-sm">+ New Job Description</Link>
                    <Link href="/dashboard/candidates" className="btn-secondary text-sm">Import Candidates</Link>
                    <Link href="/dashboard/search" className="btn-secondary text-sm">AI Search</Link>
                </div>
            </div>
        </div>
    );
}

function DashboardSkeleton() {
    return (
        <div className="animate-fade-in">
            <div className="h-10 w-48 skeleton rounded-lg mb-8" />
            <div className="grid grid-cols-4 gap-5 mb-8">
                {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="h-32 skeleton rounded-2xl" />
                ))}
            </div>
            <div className="grid grid-cols-2 gap-6">
                <div className="h-48 skeleton rounded-2xl" />
                <div className="h-48 skeleton rounded-2xl" />
            </div>
        </div>
    );
}
