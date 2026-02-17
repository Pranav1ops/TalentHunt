'use client';
import { useState, useEffect } from 'react';
import { analyticsApi } from '@/lib/api';

export default function AnalyticsPage() {
    const [overview, setOverview] = useState<any>(null);
    const [rediscovery, setRediscovery] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([
            analyticsApi.overview(),
            analyticsApi.rediscovery(),
        ]).then(([o, r]) => {
            setOverview(o);
            setRediscovery(r);
        }).finally(() => setLoading(false));
    }, []);

    if (loading) return (
        <div className="space-y-6">
            <div className="h-10 w-48 skeleton rounded-lg" />
            <div className="grid grid-cols-4 gap-4">{[1, 2, 3, 4].map(i => <div key={i} className="h-28 skeleton rounded-2xl" />)}</div>
            <div className="grid grid-cols-2 gap-6">{[1, 2].map(i => <div key={i} className="h-64 skeleton rounded-2xl" />)}</div>
        </div>
    );

    const signalTypeLabels: Record<string, { label: string; color: string; emoji: string }> = {
        previously_rejected_similar: { label: 'Previously Rejected', color: 'bg-red-500', emoji: '🔄' },
        skills_now_trending: { label: 'Trending Skills', color: 'bg-purple-500', emoji: '📈' },
        now_available: { label: 'Now Available', color: 'bg-green-500', emoji: '✅' },
        long_inactive_strong_match: { label: 'Hidden Talent', color: 'bg-blue-500', emoji: '💎' },
        near_miss: { label: 'Near Miss', color: 'bg-amber-500', emoji: '🎯' },
        recent_upskilling: { label: 'Recent Upskilling', color: 'bg-cyan-500', emoji: '🚀' },
        similar_role_history: { label: 'Similar Roles', color: 'bg-pink-500', emoji: '📋' },
    };

    const totalSignals = rediscovery?.total_signals || 0;

    return (
        <div className="animate-fade-in">
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-dark-100 mb-1">Analytics</h1>
                <p className="text-dark-400 text-sm">Track rediscovery success and recruiter activity</p>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <MetricCard label="Total Candidates" value={overview?.total_candidates || 0} gradient="from-blue-500/20 to-cyan-500/20" />
                <MetricCard label="Rediscovery Rate" value={`${rediscovery?.rediscovery_rate || 0}%`} gradient="from-purple-500/20 to-pink-500/20" />
                <MetricCard label="Total Signals" value={totalSignals} gradient="from-amber-500/20 to-orange-500/20" />
                <MetricCard label="Avg Match Score" value={overview?.avg_match_score || 0} gradient="from-emerald-500/20 to-teal-500/20" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {/* Rediscovery Signals Breakdown */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold text-dark-200 mb-5">Rediscovery Signals by Type</h3>
                    <div className="space-y-4">
                        {Object.entries(rediscovery?.signals_by_type || {}).map(([type, count]) => {
                            const meta = signalTypeLabels[type] || { label: type, color: 'bg-gray-500', emoji: '📊' };
                            const pct = totalSignals > 0 ? ((count as number) / totalSignals) * 100 : 0;
                            return (
                                <div key={type}>
                                    <div className="flex items-center justify-between mb-1.5">
                                        <span className="text-sm text-dark-300 flex items-center gap-2">
                                            <span>{meta.emoji}</span> {meta.label}
                                        </span>
                                        <span className="text-sm text-dark-400">{count as number} ({pct.toFixed(0)}%)</span>
                                    </div>
                                    <div className="score-bar h-3">
                                        <div className={`score-fill ${meta.color}`} style={{ width: `${pct}%` }} />
                                    </div>
                                </div>
                            );
                        })}
                        {Object.keys(rediscovery?.signals_by_type || {}).length === 0 && (
                            <p className="text-dark-500 text-sm">No signals detected yet. Run AI matching on a job description to generate rediscovery signals.</p>
                        )}
                    </div>
                </div>

                {/* Top Skills Distribution */}
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold text-dark-200 mb-5">Top Skills in Database</h3>
                    <div className="space-y-3">
                        {(overview?.top_skills || []).slice(0, 8).map((s: any, idx: number) => {
                            const maxCount = overview?.top_skills?.[0]?.count || 1;
                            const pct = (s.count / maxCount) * 100;
                            const colors = ['from-primary-500 to-purple-500', 'from-cyan-500 to-blue-500', 'from-emerald-500 to-teal-500', 'from-amber-500 to-orange-500'];
                            return (
                                <div key={s.skill} className="flex items-center gap-3">
                                    <span className="text-sm text-dark-300 w-28 truncate capitalize">{s.skill}</span>
                                    <div className="flex-1 score-bar h-3">
                                        <div className={`score-fill bg-gradient-to-r ${colors[idx % colors.length]}`} style={{ width: `${pct}%` }} />
                                    </div>
                                    <span className="text-xs text-dark-500 w-8 text-right">{s.count}</span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>

            {/* Top Rediscovered Candidates */}
            {(rediscovery?.top_rediscovered_candidates || []).length > 0 && (
                <div className="glass-card p-6">
                    <h3 className="text-lg font-semibold text-dark-200 mb-4">Top Rediscovered Candidates</h3>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="text-left text-xs text-dark-500 uppercase border-b border-dark-700/50">
                                    <th className="pb-3 pr-4">Candidate ID</th>
                                    <th className="pb-3 pr-4">Signals</th>
                                    <th className="pb-3 pr-4">Total Boost</th>
                                </tr>
                            </thead>
                            <tbody>
                                {(rediscovery?.top_rediscovered_candidates || []).map((c: any) => (
                                    <tr key={c.candidate_id} className="border-b border-dark-800/30">
                                        <td className="py-3 pr-4 text-sm text-dark-300 font-mono">{c.candidate_id?.slice(0, 8)}...</td>
                                        <td className="py-3 pr-4">
                                            <span className="badge-primary">{c.signal_count} signals</span>
                                        </td>
                                        <td className="py-3 pr-4 text-sm text-accent-400 font-semibold">+{c.total_boost}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}

function MetricCard({ label, value, gradient }: { label: string; value: number | string; gradient: string }) {
    return (
        <div className={`glass-card p-5 bg-gradient-to-br ${gradient}`}>
            <div className="text-2xl font-bold text-dark-100 mb-1">{value}</div>
            <div className="text-sm text-dark-400">{label}</div>
        </div>
    );
}
