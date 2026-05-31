import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { ThemeProvider } from '@/components/theme-provider';

const inter = Inter({ subsets: ['latin'], variable: '--font-sans' });

export const metadata: Metadata = {
  title: {
    default: 'Infinity Interns™ — India\'s Engineering Internship Platform',
    template: '%s · Infinity Interns',
  },
  description:
    'Discover, apply, track, complete, and earn verified internships across 30+ engineering branches and 35+ technology domains.',
  keywords: ['internships', 'engineering', 'india', 'certificates', 'students', 'recruiting'],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
