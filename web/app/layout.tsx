import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'Esports Atlas | Competitive Statistics', description: 'Historical statistics for VALORANT, League of Legends and Counter-Strike 2.' };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="es"><body>{children}</body></html>; }
