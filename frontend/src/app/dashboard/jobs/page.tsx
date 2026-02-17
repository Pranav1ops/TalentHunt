'use client';
import { useState, useEffect } from 'react';
import { jobsApi } from '@/lib/api';
import Link from 'next/link';

export default function JobsPage() {
    const [jobs, setJobs] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreate, setShowCreate] = useState(false);
    const [form, setForm] = useState({ title: '', raw_text: '' });
    const [creating, setCreating] = useState(false);
    const [uploadFile, setUploadFile] = useState<File | null>(null);

    const fetchJobs = () => {
        jobsApi.list()
            .then((res) => setJobs(res.jobs || []))
            .catch(() => { })
            .finally(() => setLoading(false));
    };

    useEffect(() => { fetchJobs(); }, []);

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        setCreating(true);
        try {
            if (uploadFile) {
                await jobsApi.upload(form.title, uploadFile);
            } else {
                await jobsApi.create({ title: form.title, raw_text: form.raw_text });
            }
            setShowCreate(false);
            setForm({ title: '', raw_text: '' });
            setUploadFile(null);
            fetchJobs();
        } catch (err: any) {
            alert(err.message);
        } finally {
            setCreating(false);
        }
    };

    return (
        <div className="animate-fade-in">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-dark-100 mb-1">Job Descriptions</h1>
                    <p className="text-dark-400 text-sm">Create and manage job descriptions for AI matching</p>
                </div>
                <button onClick={() => setShowCreate(!showCreate)} className="btn-primary">
                    + New Job
                </button>
            </div>

            {/* Create Form */}
            {showCreate && (
                <div className="glass-card p-6 mb-8 animate-slide-up">
                    <h3 className="text-lg font-semibold text-dark-200 mb-4">Create Job Description</h3>
                    <form onSubmit={handleCreate} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-dark-300 mb-2">Job Title</label>
                            <input
                                id="jd-title"
                                type="text"
                                value={form.title}
                                onChange={(e) => setForm({ ...form, title: e.target.value })}
                                className="input-field"
                                placeholder="e.g. Senior Python Developer"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-dark-300 mb-2">Job Description</label>
                            <textarea
                                id="jd-text"
                                value={form.raw_text}
                                onChange={(e) => setForm({ ...form, raw_text: e.target.value })}
                                className="input-field min-h-[200px] font-mono text-sm"
                                placeholder="Paste the full job description here..."
                                required={!uploadFile}
                            />
                        </div>
                        <div className="flex items-center gap-4">
                            <span className="text-sm text-dark-400">Or upload a file:</span>
                            <input
                                id="jd-upload"
                                type="file"
                                accept=".pdf,.docx,.txt"
                                onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                                className="text-sm text-dark-300 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:bg-dark-700 file:text-dark-200 hover:file:bg-dark-600"
                            />
                        </div>
                        <div className="flex gap-3">
                            <button type="submit" disabled={creating} className="btn-primary">
                                {creating ? 'Creating...' : 'Create & Parse'}
                            </button>
                            <button type="button" onClick={() => setShowCreate(false)} className="btn-secondary">
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Jobs List */}
            {loading ? (
                <div className="space-y-4">
                    {[1, 2, 3].map((i) => <div key={i} className="h-24 skeleton rounded-2xl" />)}
                </div>
            ) : jobs.length === 0 ? (
                <div className="glass-card p-12 text-center">
                    <div className="text-5xl mb-4">📋</div>
                    <h3 className="text-lg font-medium text-dark-300 mb-2">No job descriptions yet</h3>
                    <p className="text-dark-500 text-sm mb-4">Create your first JD to start discovering candidates</p>
                    <button onClick={() => setShowCreate(true)} className="btn-primary">Create Job Description</button>
                </div>
            ) : (
                <div className="space-y-4">
                    {jobs.map((job) => (
                        <Link
                            key={job.id}
                            href={`/dashboard/jobs/${job.id}`}
                            className="glass-card-hover p-5 block"
                        >
                            <div className="flex items-center justify-between">
                                <div className="flex-1">
                                    <h3 className="text-lg font-semibold text-dark-100 mb-1">{job.title}</h3>
                                    <div className="flex items-center gap-4 text-sm text-dark-400">
                                        <span className={`badge ${job.status === 'active' ? 'badge-accent' : 'badge-warning'}`}>
                                            {job.status}
                                        </span>
                                        {job.parsed_data?.skills?.mandatory && (
                                            <span>{job.parsed_data.skills.mandatory.length} required skills</span>
                                        )}
                                        {job.parsed_data?.seniority && <span>• {job.parsed_data.seniority}</span>}
                                        {job.parsed_data?.location && <span>• {job.parsed_data.location}</span>}
                                        <span>• {new Date(job.created_at).toLocaleDateString()}</span>
                                    </div>
                                </div>
                                <svg className="w-5 h-5 text-dark-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                </svg>
                            </div>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
}
