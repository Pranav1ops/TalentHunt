const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

interface FetchOptions extends RequestInit {
    token?: string;
}

async function apiFetch<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
    const { token, headers: customHeaders, ...rest } = options;

    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...((customHeaders as Record<string, string>) || {}),
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    } else if (typeof window !== 'undefined') {
        const stored = localStorage.getItem('token');
        if (stored) headers['Authorization'] = `Bearer ${stored}`;
    }

    const res = await fetch(`${API_BASE}${endpoint}`, { headers, ...rest });

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || `HTTP ${res.status}`);
    }

    if (res.status === 204) return {} as T;
    return res.json();
}

// Multipart upload (no Content-Type header — let browser set boundary)
async function apiUpload<T>(endpoint: string, formData: FormData): Promise<T> {
    const headers: Record<string, string> = {};
    if (typeof window !== 'undefined') {
        const stored = localStorage.getItem('token');
        if (stored) headers['Authorization'] = `Bearer ${stored}`;
    }

    const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers,
        body: formData,
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: 'Upload failed' }));
        throw new Error(error.detail || `HTTP ${res.status}`);
    }
    return res.json();
}

// Auth
export const authApi = {
    register: (data: { company_name: string; name: string; email: string; password: string }) =>
        apiFetch<any>('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
    login: (data: { email: string; password: string }) =>
        apiFetch<any>('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
    me: () => apiFetch<any>('/auth/me'),
};

// Jobs
export const jobsApi = {
    list: () => apiFetch<any>('/jobs/'),
    get: (id: string) => apiFetch<any>(`/jobs/${id}`),
    create: (data: { title: string; raw_text: string }) =>
        apiFetch<any>('/jobs/', { method: 'POST', body: JSON.stringify(data) }),
    upload: (title: string, file: File) => {
        const fd = new FormData();
        fd.append('file', file);
        fd.append('title', title);
        return apiUpload<any>(`/jobs/upload?title=${encodeURIComponent(title)}`, fd);
    },
    parse: (id: string) =>
        apiFetch<any>(`/jobs/${id}/parse`, { method: 'POST' }),
    delete: (id: string) =>
        apiFetch<any>(`/jobs/${id}`, { method: 'DELETE' }),
};

// Candidates
export const candidatesApi = {
    list: (params?: { page?: number; per_page?: number; search?: string; status?: string }) => {
        const query = new URLSearchParams();
        if (params?.page) query.set('page', String(params.page));
        if (params?.per_page) query.set('per_page', String(params.per_page));
        if (params?.search) query.set('search', params.search);
        if (params?.status) query.set('status', params.status);
        return apiFetch<any>(`/candidates/?${query.toString()}`);
    },
    get: (id: string) => apiFetch<any>(`/candidates/${id}`),
    create: (data: any) =>
        apiFetch<any>('/candidates/', { method: 'POST', body: JSON.stringify(data) }),
    import: (file: File) => {
        const fd = new FormData();
        fd.append('file', file);
        return apiUpload<any>('/candidates/import', fd);
    },
    update: (id: string, data: any) =>
        apiFetch<any>(`/candidates/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
};

// Matches
export const matchesApi = {
    compute: (jobId: string) =>
        apiFetch<any>(`/matches/compute/${jobId}`, { method: 'POST' }),
    results: (jobId: string) =>
        apiFetch<any>(`/matches/${jobId}/results`),
};

// Actions
export const actionsApi = {
    create: (data: { candidate_id: string; job_id?: string; action: string; notes?: string }) =>
        apiFetch<any>('/actions/', { method: 'POST', body: JSON.stringify(data) }),
    candidateHistory: (candidateId: string) =>
        apiFetch<any>(`/actions/candidate/${candidateId}`),
};

// Analytics
export const analyticsApi = {
    overview: () => apiFetch<any>('/analytics/overview'),
    rediscovery: () => apiFetch<any>('/analytics/rediscovery'),
};

// Search
export const searchApi = {
    agent: (query: string) =>
        apiFetch<any>('/search/agent', { method: 'POST', body: JSON.stringify({ query }) }),
};
