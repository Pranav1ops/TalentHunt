'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';

export default function Home() {
    const router = useRouter();
    const { user, isLoading } = useAuth();

    useEffect(() => {
        if (!isLoading) {
            router.replace(user ? '/dashboard' : '/login');
        }
    }, [user, isLoading, router]);

    return (
        <div className="min-h-screen flex items-center justify-center">
            <div className="animate-pulse-soft">
                <div className="w-12 h-12 rounded-full bg-gradient-to-r from-primary-500 to-primary-600 animate-spin" style={{ animationDuration: '1.5s' }} />
            </div>
        </div>
    );
}
