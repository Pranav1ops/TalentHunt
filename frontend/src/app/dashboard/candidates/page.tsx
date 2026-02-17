'use client';
import { useState, useEffect } from 'react';
import { candidatesApi } from '@/lib/api';
import Link from 'next/link';

export default function CandidatesPage() {
    const [candidates, setCandidates] = useState<any[]>([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(true);
    const [importing, setImporting] = useState(false);

    const fetchCandidates = (p = page, s = search) => {
        setLoading(true);
        candidatesApi.list({ page: p, per_page: 20, search: s || undefined })
            .then((res) => { setCandidates(res.candidates || []); setTotal(res.total || 0); })
            .catch(() => { })
            .finally(() => setLoading(false));
    };

    useEffect(() => { fetchCandidates(); }, []);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        setPage(1);
        fetchCandidates(1, search);
    };

    const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;
        setImporting(true);
        try {
            const result = await candidatesApi.import(file);
            alert(`Imported ${result.imported} candidates`);
            fetchCandidates();
        } catch (err: any) {
            alert(err.message);
        } finally {
            setImporting(false);
        }
    };

    const statusColors: Record<string, string> = {
        available: 'badge-accent',
        open_to_offers: 'badge-primary',
        employed: 'badge-warning',
        unavailable: 'badge-danger',
    };

    return (
        <div className="animate-fade-in">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-dark-100 mb-1">Candidates</h1>
                    <p className="text-dark-400 text-sm">{total} candidates in database</p>
                </div>
                <div className="flex gap-3">
                    <label className={`btn-secondary cursor-pointer ${importing ? 'opacity-50' : ''}`}>
                        {importing ? 'Importing...' : '📁 Import CSV/XLSX'}
                        <input type="file" accept=".csv,.xlsx,.xls" onChange={handleImport} className="hidden" />
                    </label>
                </div>
            </div>

            {/* Search */}
            <form onSubmit={handleSearch} className="mb-6">
                <div className="flex gap-3">
                    <input
                        id="candidate-search"
                        type="text"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="input-field flex-1"
                        placeholder="Search by name or email..."
                    />
                    <button type="submit" className="btn-primary">Search</button>
                </div>
            </form>

            {/* Candidates List */}
            {loading ? (
                <div className="space-y-3">{[1, 2, 3, 4, 5].map((i) => <div key={i} className="h-20 skeleton rounded-2xl" />)}</div>
            ) : candidates.length === 0 ? (
                <div className="glass-card p-12 text-center">
                    <div className="text-5xl mb-4">👥</div>
                    <h3 className="text-lg font-medium text-dark-300 mb-2">No candidates found</h3>
                    <p className="text-dark-500 text-sm">Import candidates via CSV/XLSX to get started</p>
                </div>
            ) : (
                <div className="space-y-3">
                    {candidates.map((c, idx) => (
                        <Link
                            key={c.id}
                            href={`/dashboard/candidates/${c.id}`}
                            className="glass-card-hover p-4 block animate-slide-up"
                            style={{ animationDelay: `${idx * 30}ms` }}
                        >
                            <div className="flex items-center gap-4">
                                <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-primary-500/30 to-purple-500/30 flex items-center justify-center text-primary-200 font-bold text-sm flex-shrink-0">
                                    {c.name?.charAt(0) || '?'}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-3 mb-1">
                                        <span className="font-semibold text-dark-100">{c.name}</span>
                                        <span className={statusColors[c.current_status] || 'badge'}>{c.current_status}</span>
                                        {c.seniority && <span className="text-xs text-dark-500 capitalize">{c.seniority}</span>}
                                    </div>
                                    <div className="flex items-center gap-3 text-sm text-dark-400">
                                        {c.location && <span>📍 {c.location}</span>}
                                        {c.experience_years > 0 && <span>• {c.experience_years} yrs</span>}
                                        {c.email && <span>• {c.email}</span>}
                                    </div>
                                </div>
                                <div className="flex flex-wrap gap-1 max-w-xs justify-end">
                                    {(c.skills || []).slice(0, 5).map((s: string) => (
                                        <span key={s} className="badge-primary text-xs">{s}</span>
                                    ))}
                                    {(c.skills || []).length > 5 && <span className="text-xs text-dark-500">+{c.skills.length - 5}</span>}
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>
            )}

            {/* Pagination */}
            {total > 20 && (
                <div className="flex justify-center gap-2 mt-6">
                    <button
                        onClick={() => { setPage(page - 1); fetchCandidates(page - 1); }}
                        disabled={page <= 1}
                        className="btn-secondary disabled:opacity-30"
                    >
                        Previous
                    </button>
                    <span className="px-4 py-2 text-sm text-dark-400">Page {page} of {Math.ceil(total / 20)}</span>
                    <button
                        onClick={() => { setPage(page + 1); fetchCandidates(page + 1); }}
                        disabled={page >= Math.ceil(total / 20)}
                        className="btn-secondary disabled:opacity-30"
                    >
                        Next
                    </button>
                </div>
            )}
        </div>
    );
}
