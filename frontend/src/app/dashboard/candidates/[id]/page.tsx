'use client';
import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { candidatesApi, actionsApi } from '@/lib/api';

export default function CandidateDetailPage() {
    const params = useParams();
    const router = useRouter();
    const candidateId = params.id as string;
    const [candidate, setCandidate] = useState<any>(null);
    const [interactions, setInteractions] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState('');

    useEffect(() => {
        Promise.all([
            candidatesApi.get(candidateId),
            actionsApi.candidateHistory(candidateId).catch(() => []),
        ]).then(([c, i]) => {
            setCandidate(c);
            setInteractions(Array.isArray(i) ? i : []);
        }).finally(() => setLoading(false));
    }, [candidateId]);

    const handleAction = async (action: string) => {
        setActionLoading(action);
        try {
            await actionsApi.create({ candidate_id: candidateId, action });
            const i = await actionsApi.candidateHistory(candidateId).catch(() => []);
            setInteractions(Array.isArray(i) ? i : []);
        } catch (err: any) {
            alert(err.message);
        } finally {
            setActionLoading('');
        }
    };

    if (loading) return <div className="flex justify-center py-20"><div className="w-10 h-10 border-3 border-primary-500/30 border-t-primary-500 rounded-full animate-spin" /></div>;
    if (!candidate) return <div className="text-center py-20 text-dark-400">Candidate not found</div>;

    const skills = candidate.skills || [];
    const statusColors: Record<string, string> = {
        available: 'text-accent-400 bg-accent-500/10', open_to_offers: 'text-primary-400 bg-primary-500/10',
        employed: 'text-amber-400 bg-amber-500/10', unavailable: 'text-red-400 bg-red-500/10',
    };

    // AI talking points
    const talkingPoints = generateTalkingPoints(candidate);

    return (
        <div className="animate-fade-in">
            <button onClick={() => router.back()} className="text-dark-400 hover:text-dark-200 text-sm flex items-center gap-1 mb-6">← Back</button>

            {/* Header */}
            <div className="glass-card p-6 mb-6">
                <div className="flex items-start justify-between">
                    <div className="flex items-center gap-5">
                        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold shadow-lg shadow-primary-500/30">
                            {candidate.name?.charAt(0)}
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-dark-100 mb-1">{candidate.name}</h1>
                            <div className="flex items-center gap-3 text-sm text-dark-400">
                                {candidate.email && <span>📧 {candidate.email}</span>}
                                {candidate.phone && <span>• 📱 {candidate.phone}</span>}
                            </div>
                            <div className="flex items-center gap-3 mt-2">
                                <span className={`badge ${statusColors[candidate.current_status] || ''}`}>{candidate.current_status}</span>
                                {candidate.seniority && <span className="badge-primary capitalize">{candidate.seniority}</span>}
                                {candidate.location && <span className="text-sm text-dark-400">📍 {candidate.location}</span>}
                            </div>
                        </div>
                    </div>
                    {/* Actions */}
                    <div className="flex gap-2">
                        {['contacted', 'pipelined', 'saved', 'rejected'].map((action) => (
                            <button
                                key={action}
                                onClick={() => handleAction(action)}
                                disabled={!!actionLoading}
                                className={`${action === 'rejected' ? 'btn-danger' : action === 'contacted' ? 'btn-primary' : 'btn-secondary'} text-sm capitalize`}
                            >
                                {actionLoading === action ? '...' : action === 'contacted' ? '📞 Contact' : action === 'pipelined' ? '📋 Pipeline' : action === 'saved' ? '💾 Save' : '✖ Reject'}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Profile Details */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Skills Heatmap */}
                    <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold text-dark-200 mb-4">Skill Profile</h3>
                        <div className="flex flex-wrap gap-2">
                            {skills.map((s: string, i: number) => {
                                const intensity = Math.min(100, 40 + (skills.length - i) * 8);
                                return (
                                    <span
                                        key={s}
                                        className="px-3 py-1.5 rounded-lg text-sm font-medium transition-all hover:scale-105"
                                        style={{
                                            backgroundColor: `hsla(250, 70%, ${intensity}%, 0.15)`,
                                            color: `hsl(250, 70%, ${Math.min(85, intensity + 20)}%)`,
                                            borderWidth: '1px',
                                            borderColor: `hsla(250, 70%, ${intensity}%, 0.25)`,
                                        }}
                                    >
                                        {s}
                                    </span>
                                );
                            })}
                        </div>
                    </div>

                    {/* Profile Info Grid */}
                    <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold text-dark-200 mb-4">Profile Details</h3>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-5">
                            <InfoItem label="Experience" value={`${candidate.experience_years} years`} />
                            <InfoItem label="Availability" value={candidate.availability} />
                            <InfoItem label="Salary Expectation" value={candidate.salary_expectation ? `${candidate.salary_currency} ${candidate.salary_expectation.toLocaleString()}` : 'Not specified'} />
                            <InfoItem label="Industry" value={candidate.industry || 'Not specified'} />
                            <InfoItem label="Remote" value={candidate.open_to_remote === 'true' ? 'Yes' : 'No'} />
                            <InfoItem label="Last Interaction" value={candidate.last_interaction ? new Date(candidate.last_interaction).toLocaleDateString() : 'Never'} />
                        </div>
                    </div>

                    {/* Notes */}
                    {candidate.notes && (
                        <div className="glass-card p-6">
                            <h3 className="text-lg font-semibold text-dark-200 mb-3">Notes</h3>
                            <p className="text-dark-300 text-sm leading-relaxed">{candidate.notes}</p>
                        </div>
                    )}

                    {/* Previous Submissions */}
                    {candidate.previous_submissions?.length > 0 && (
                        <div className="glass-card p-6">
                            <h3 className="text-lg font-semibold text-dark-200 mb-4">Previous Submissions</h3>
                            <div className="space-y-3">
                                {candidate.previous_submissions.map((sub: any, idx: number) => (
                                    <div key={idx} className="flex items-center gap-4 p-3 rounded-lg bg-dark-900/40">
                                        <div className="flex-1">
                                            <div className="text-sm font-medium text-dark-200">{sub.job_title}</div>
                                            <div className="text-xs text-dark-500">{sub.date}</div>
                                        </div>
                                        <span className={`badge ${sub.outcome === 'rejected' ? 'badge-danger' : sub.outcome === 'shortlisted' || sub.outcome === 'interviewed' ? 'badge-accent' : 'badge-warning'}`}>
                                            {sub.outcome}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Right Column */}
                <div className="space-y-6">
                    {/* AI Talking Points */}
                    <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold text-dark-200 mb-3 flex items-center gap-2">
                            🤖 AI Talking Points
                        </h3>
                        <div className="space-y-3">
                            {talkingPoints.map((tp, idx) => (
                                <div key={idx} className="p-3 rounded-lg bg-primary-500/5 border border-primary-500/10">
                                    <p className="text-sm text-dark-300">{tp}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Risk Indicators */}
                    <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold text-dark-200 mb-3">Risk Indicators</h3>
                        <div className="space-y-2">
                            {generateRiskIndicators(candidate).map((risk, idx) => (
                                <div key={idx} className={`flex items-center gap-2 text-sm ${risk.level === 'high' ? 'text-red-400' : risk.level === 'medium' ? 'text-amber-400' : 'text-accent-400'}`}>
                                    <span>{risk.level === 'high' ? '🔴' : risk.level === 'medium' ? '🟡' : '🟢'}</span>
                                    <span>{risk.text}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Interaction Timeline */}
                    <div className="glass-card p-6">
                        <h3 className="text-lg font-semibold text-dark-200 mb-4">Interaction Timeline</h3>
                        {interactions.length === 0 ? (
                            <p className="text-dark-500 text-sm">No interactions recorded</p>
                        ) : (
                            <div className="space-y-3">
                                {interactions.slice(0, 10).map((i: any) => (
                                    <div key={i.id} className="flex items-center gap-3 text-sm">
                                        <div className="w-2 h-2 rounded-full bg-primary-500 flex-shrink-0" />
                                        <div className="flex-1">
                                            <span className="text-dark-200 capitalize font-medium">{i.action}</span>
                                            {i.notes && <span className="text-dark-500"> — {i.notes}</span>}
                                        </div>
                                        <span className="text-xs text-dark-500">{new Date(i.created_at).toLocaleDateString()}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

function InfoItem({ label, value }: { label: string; value: string }) {
    return (
        <div>
            <div className="text-xs text-dark-500 mb-1">{label}</div>
            <div className="text-sm text-dark-200 font-medium">{value}</div>
        </div>
    );
}

function generateTalkingPoints(c: any): string[] {
    const points: string[] = [];
    if (c.experience_years >= 5) points.push(`With ${c.experience_years} years of experience, ${c.name.split(' ')[0]} brings deep expertise to the table.`);
    if (c.skills?.length > 5) points.push(`Strong multi-skill profile covering ${c.skills.slice(0, 3).join(', ')} and ${c.skills.length - 3} more technologies.`);
    if (c.current_status === 'available') points.push('Currently available and open to new opportunities — optimal timing for outreach.');
    if (c.open_to_remote === 'true') points.push('Open to remote work, providing flexibility in role placement.');
    if (c.previous_submissions?.length > 0) points.push(`Has history with your agency (${c.previous_submissions.length} previous submissions) — established rapport.`);
    if (c.industry) points.push(`Domain expertise in ${c.industry} — valuable for industry-specific roles.`);
    if (points.length === 0) points.push('Consider reaching out to learn more about their current situation and interests.');
    return points;
}

function generateRiskIndicators(c: any): { text: string; level: string }[] {
    const risks: { text: string; level: string }[] = [];
    if (c.current_status === 'unavailable') risks.push({ text: 'Currently marked as unavailable', level: 'high' });
    if (c.current_status === 'employed') risks.push({ text: 'Currently employed — may need longer notice', level: 'medium' });
    if (c.salary_expectation && c.salary_expectation > 3000000) risks.push({ text: 'Higher salary expectation', level: 'medium' });
    if (!c.last_interaction) risks.push({ text: 'Never contacted — unknown engagement', level: 'medium' });
    if (c.current_status === 'available') risks.push({ text: 'Actively available — lower risk', level: 'low' });
    if (c.experience_years >= 5) risks.push({ text: 'Experienced candidate — reliable profile', level: 'low' });
    return risks;
}
