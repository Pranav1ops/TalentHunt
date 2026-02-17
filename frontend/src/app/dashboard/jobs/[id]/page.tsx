'use client';
import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { jobsApi, matchesApi } from '@/lib/api';

export default function JobDetailPage() {
    const params = useParams();
    const router = useRouter();
    const jobId = params.id as string;
    const [job, setJob] = useState<any>(null);
    const [matches, setMatches] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [computing, setComputing] = useState(false);
    const [activeTab, setActiveTab] = useState<'details' | 'matches'>('details');

    useEffect(() => {
        Promise.all([
            jobsApi.get(jobId),
            matchesApi.results(jobId).catch(() => null),
        ]).then(([j, m]) => {
            setJob(j);
            setMatches(m);
        }).finally(() => setLoading(false));
    }, [jobId]);

    const runMatching = async () => {
        setComputing(true);
        try {
            await matchesApi.compute(jobId);
            const m = await matchesApi.results(jobId);
            setMatches(m);
            setActiveTab('matches');
        } catch (err: any) {
            alert(err.message);
        } finally {
            setComputing(false);
        }
    };

    if (loading) return <div className="flex justify-center py-20"><div className="w-10 h-10 border-3 border-primary-500/30 border-t-primary-500 rounded-full animate-spin" /></div>;
    if (!job) return <div className="text-center py-20 text-dark-400">Job not found</div>;

    const parsed = job.parsed_data || {};

    return (
        <div className="animate-fade-in">
            {/* Header */}
            <div className="flex items-start justify-between mb-8">
                <div>
                    <button onClick={() => router.back()} className="text-dark-400 hover:text-dark-200 text-sm flex items-center gap-1 mb-3">
                        ← Back to Jobs
                    </button>
                    <h1 className="text-2xl font-bold text-dark-100 mb-2">{job.title}</h1>
                    <div className="flex items-center gap-3">
                        <span className={`badge ${job.status === 'active' ? 'badge-accent' : 'badge-warning'}`}>{job.status}</span>
                        <span className="text-sm text-dark-400">{new Date(job.created_at).toLocaleDateString()}</span>
                    </div>
                </div>
                <button onClick={runMatching} disabled={computing} className="btn-primary flex items-center gap-2">
                    {computing ? (
                        <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Computing...</>
                    ) : (
                        <>🎯 Run AI Matching</>
                    )}
                </button>
            </div>

            {/* Tabs */}
            <div className="flex gap-1 mb-6 bg-dark-800/40 p-1 rounded-xl w-fit">
                <button
                    onClick={() => setActiveTab('details')}
                    className={`px-5 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === 'details' ? 'bg-primary-500/20 text-primary-300' : 'text-dark-400 hover:text-dark-200'}`}
                >
                    Parsed Details
                </button>
                <button
                    onClick={() => setActiveTab('matches')}
                    className={`px-5 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === 'matches' ? 'bg-primary-500/20 text-primary-300' : 'text-dark-400 hover:text-dark-200'}`}
                >
                    Match Results {matches?.total ? `(${matches.total})` : ''}
                </button>
            </div>

            {activeTab === 'details' ? (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Parsed Data */}
                    <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold text-dark-200 mb-4">AI-Parsed Requirements</h3>
                        <div className="space-y-4">
                            {parsed.skills?.mandatory?.length > 0 && (
                                <div>
                                    <div className="text-xs font-medium text-dark-400 uppercase mb-2">Required Skills</div>
                                    <div className="flex flex-wrap gap-2">
                                        {parsed.skills.mandatory.map((s: string) => (
                                            <span key={s} className="badge-primary">{s}</span>
                                        ))}
                                    </div>
                                </div>
                            )}
                            {parsed.skills?.optional?.length > 0 && (
                                <div>
                                    <div className="text-xs font-medium text-dark-400 uppercase mb-2">Nice to Have</div>
                                    <div className="flex flex-wrap gap-2">
                                        {parsed.skills.optional.map((s: string) => (
                                            <span key={s} className="badge-warning">{s}</span>
                                        ))}
                                    </div>
                                </div>
                            )}
                            <div className="grid grid-cols-2 gap-4 pt-2">
                                {parsed.seniority && <DetailItem label="Seniority" value={parsed.seniority} />}
                                {parsed.experience_range && <DetailItem label="Experience" value={`${parsed.experience_range.min}-${parsed.experience_range.max} years`} />}
                                {parsed.location && <DetailItem label="Location" value={parsed.location} />}
                                {parsed.domain && <DetailItem label="Domain" value={parsed.domain} />}
                                {parsed.industry && <DetailItem label="Industry" value={parsed.industry} />}
                                {parsed.salary_band && <DetailItem label="Salary" value={`${parsed.salary_band.currency} ${parsed.salary_band.min?.toLocaleString()}`} />}
                            </div>
                        </div>
                    </div>

                    {/* Raw JD */}
                    <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold text-dark-200 mb-4">Raw Description</h3>
                        <pre className="text-sm text-dark-300 whitespace-pre-wrap font-mono leading-relaxed max-h-96 overflow-y-auto">
                            {job.raw_text}
                        </pre>
                    </div>
                </div>
            ) : (
                /* Match Results */
                <MatchResults matches={matches} jobId={jobId} />
            )}
        </div>
    );
}

function DetailItem({ label, value }: { label: string; value: string }) {
    return (
        <div>
            <div className="text-xs text-dark-500 mb-1">{label}</div>
            <div className="text-sm text-dark-200 font-medium capitalize">{value}</div>
        </div>
    );
}

function MatchResults({ matches, jobId }: { matches: any; jobId: string }) {
    if (!matches || !matches.matches?.length) {
        return (
            <div className="glass-card p-12 text-center">
                <div className="text-5xl mb-4">🎯</div>
                <h3 className="text-lg font-medium text-dark-300 mb-2">No matches computed yet</h3>
                <p className="text-dark-500 text-sm">Click "Run AI Matching" to score candidates against this job</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {matches.matches.map((m: any, idx: number) => (
                <div key={m.id} className="glass-card-hover p-5 animate-slide-up" style={{ animationDelay: `${idx * 50}ms` }}>
                    <div className="flex items-start gap-5">
                        {/* Rank */}
                        <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500/20 to-purple-500/20 flex items-center justify-center text-primary-300 font-bold text-sm">
                            #{idx + 1}
                        </div>

                        {/* Candidate Info */}
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-3 mb-2">
                                <Link href={`/dashboard/candidates/${m.candidate_id}`} className="text-lg font-semibold text-dark-100 hover:text-primary-300 transition-colors">
                                    {m.candidate?.name || 'Unknown'}
                                </Link>
                                {m.rediscovery_signals?.length > 0 && (
                                    <span className="badge bg-gradient-to-r from-amber-500/15 to-orange-500/15 text-amber-300 border-amber-500/20">
                                        ✨ {m.rediscovery_signals.length} Rediscovery Signal{m.rediscovery_signals.length > 1 ? 's' : ''}
                                    </span>
                                )}
                            </div>
                            <div className="flex items-center gap-3 text-sm text-dark-400 mb-3">
                                {m.candidate?.location && <span>📍 {m.candidate.location}</span>}
                                {m.candidate?.experience_years && <span>• {m.candidate.experience_years} yrs exp</span>}
                                {m.candidate?.seniority && <span>• {m.candidate.seniority}</span>}
                            </div>

                            {/* Skills */}
                            <div className="flex flex-wrap gap-1.5 mb-3">
                                {(m.candidate?.skills || []).slice(0, 8).map((s: string) => (
                                    <span key={s} className="badge-primary text-xs">{s}</span>
                                ))}
                            </div>

                            {/* Score Breakdown */}
                            <div className="grid grid-cols-4 gap-3 mb-3">
                                <ScoreBar label="Skills" score={m.skill_score} />
                                <ScoreBar label="Experience" score={m.experience_score} />
                                <ScoreBar label="Location" score={m.location_score} />
                                <ScoreBar label="Domain" score={m.domain_score} />
                            </div>

                            {/* Strengths & Weaknesses */}
                            {(m.strengths?.length > 0 || m.weaknesses?.length > 0) && (
                                <div className="flex gap-4 text-xs mt-2">
                                    {m.strengths?.length > 0 && (
                                        <div className="flex-1"><span className="text-accent-400 font-medium">💪 Strengths:</span>{' '}<span className="text-dark-400">{m.strengths.slice(0, 2).join('; ')}</span></div>
                                    )}
                                    {m.weaknesses?.length > 0 && (
                                        <div className="flex-1"><span className="text-red-400 font-medium">⚠️ Gaps:</span>{' '}<span className="text-dark-400">{m.weaknesses.slice(0, 2).join('; ')}</span></div>
                                    )}
                                </div>
                            )}

                            {/* Rediscovery Signals */}
                            {m.rediscovery_signals?.length > 0 && (
                                <div className="mt-3 space-y-2">
                                    {m.rediscovery_signals.map((s: any) => (
                                        <div key={s.id} className="flex items-start gap-2 p-2.5 rounded-lg bg-amber-500/5 border border-amber-500/10">
                                            <span className="text-amber-400 text-sm mt-0.5">✨</span>
                                            <div>
                                                <div className="text-xs font-medium text-amber-300 mb-0.5">{formatSignalType(s.signal_type)} (+{s.score_boost})</div>
                                                <div className="text-xs text-dark-400">{s.reason}</div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Score */}
                        <div className="flex-shrink-0 text-center">
                            <div className={`text-3xl font-bold ${getScoreColor(m.overall_score)}`}>
                                {Math.round(m.overall_score)}
                            </div>
                            <div className="text-[10px] text-dark-500 uppercase font-medium mt-1">Score</div>
                            <div className="text-xs text-dark-500 mt-1">{m.confidence}% conf.</div>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
}

function ScoreBar({ label, score }: { label: string; score: number }) {
    return (
        <div>
            <div className="flex justify-between text-xs mb-1">
                <span className="text-dark-500">{label}</span>
                <span className="text-dark-400">{Math.round(score)}</span>
            </div>
            <div className="score-bar">
                <div
                    className={`score-fill ${score >= 70 ? 'bg-accent-500' : score >= 40 ? 'bg-amber-500' : 'bg-red-400'}`}
                    style={{ width: `${score}%` }}
                />
            </div>
        </div>
    );
}

function getScoreColor(score: number): string {
    if (score >= 75) return 'text-accent-400';
    if (score >= 50) return 'text-amber-400';
    return 'text-red-400';
}

function formatSignalType(type: string): string {
    return type.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
}
