'use client';
import { useState } from 'react';
import { searchApi } from '@/lib/api';
import Link from 'next/link';

export default function SearchPage() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [history, setHistory] = useState<string[]>([]);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;
        setLoading(true);
        try {
            const res = await searchApi.agent(query);
            setResults(res);
            if (!history.includes(query)) setHistory((h) => [query, ...h.slice(0, 9)]);
        } catch (err: any) {
            alert(err.message);
        } finally {
            setLoading(false);
        }
    };

    const suggestions = [
        'Show Java devs suitable for fintech roles',
        'Who became available recently?',
        'Senior Python developers in Bangalore',
        'Candidates fit for remote roles under 20 LPA',
        'DevOps engineers with Kubernetes experience',
        'Show candidates with machine learning skills',
    ];

    return (
        <div className="animate-fade-in max-w-4xl mx-auto">
            {/* Header */}
            <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-dark-100 mb-2">AI Search Agent</h1>
                <p className="text-dark-400">Ask in natural language to find candidates in your database</p>
            </div>

            {/* Search Input */}
            <form onSubmit={handleSearch} className="mb-6">
                <div className="glass-card p-2 flex items-center gap-2">
                    <div className="pl-3">
                        <svg className="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                        </svg>
                    </div>
                    <input
                        id="search-input"
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        className="flex-1 bg-transparent border-none outline-none text-dark-100 placeholder:text-dark-500 py-3 text-lg"
                        placeholder="Ask me anything about your candidates..."
                    />
                    <button type="submit" disabled={loading} className="btn-primary">
                        {loading ? (
                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        ) : (
                            'Search'
                        )}
                    </button>
                </div>
            </form>

            {/* Suggestions */}
            {!results && (
                <div className="mb-8">
                    <div className="text-sm text-dark-500 mb-3">Try asking:</div>
                    <div className="flex flex-wrap gap-2">
                        {suggestions.map((s) => (
                            <button
                                key={s}
                                onClick={() => { setQuery(s); }}
                                className="text-sm px-4 py-2 rounded-xl bg-dark-800/50 border border-dark-700/50 text-dark-300 hover:bg-dark-700/60 hover:text-dark-100 transition-all"
                            >
                                {s}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Results */}
            {results && (
                <div className="animate-slide-up">
                    {/* Interpretation */}
                    <div className="glass-card p-4 mb-4">
                        <div className="flex items-center gap-2 text-sm">
                            <span className="text-primary-400">🤖</span>
                            <span className="text-dark-300">{results.interpretation}</span>
                            <span className="text-dark-500 ml-auto">{results.candidates?.length || 0} results</span>
                        </div>
                    </div>

                    {/* Candidate Results */}
                    {results.candidates?.length === 0 ? (
                        <div className="glass-card p-8 text-center">
                            <div className="text-4xl mb-3">🔍</div>
                            <p className="text-dark-400">No candidates match your query. Try broadening your search.</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {results.candidates.map((c: any) => (
                                <Link key={c.id} href={`/dashboard/candidates/${c.id}`} className="glass-card-hover p-4 block">
                                    <div className="flex items-center gap-4">
                                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500/30 to-purple-500/30 flex items-center justify-center text-primary-200 font-bold text-sm">
                                            {c.name?.charAt(0)}
                                        </div>
                                        <div className="flex-1">
                                            <div className="font-semibold text-dark-100">{c.name}</div>
                                            <div className="text-sm text-dark-400 flex items-center gap-2">
                                                {c.location && <span>📍 {c.location}</span>}
                                                {c.experience_years > 0 && <span>• {c.experience_years} yrs</span>}
                                                {c.seniority && <span>• {c.seniority}</span>}
                                            </div>
                                        </div>
                                        <div className="flex flex-wrap gap-1">
                                            {(c.skills || []).slice(0, 4).map((s: string) => (
                                                <span key={s} className="badge-primary text-xs">{s}</span>
                                            ))}
                                        </div>
                                    </div>
                                </Link>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Recent Searches */}
            {history.length > 0 && (
                <div className="mt-8">
                    <div className="text-sm text-dark-500 mb-3">Recent searches</div>
                    <div className="space-y-1">
                        {history.map((h) => (
                            <button
                                key={h}
                                onClick={() => setQuery(h)}
                                className="block w-full text-left text-sm px-4 py-2 rounded-lg text-dark-400 hover:text-dark-200 hover:bg-dark-800/40 transition-colors"
                            >
                                🕐 {h}
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
