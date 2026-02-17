import type { Metadata } from 'next';
import './globals.css';
import { AuthProvider } from '@/lib/auth';

export const metadata: Metadata = {
    title: 'TalentHunt — AI Candidate Rediscovery',
    description: 'AI-powered candidate rediscovery system for staffing & recruiting companies.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
        <html lang="en">
            <body className="antialiased">
                <AuthProvider>{children}</AuthProvider>
            </body>
        </html>
    );
}
