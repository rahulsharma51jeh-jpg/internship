import Link from 'next/link';
import { Infinity as InfinityIcon } from 'lucide-react';

const COLUMNS = [
  {
    title: 'Platform',
    links: [
      { href: '/internships', label: 'Browse Internships' },
      { href: '/branches', label: 'Engineering Branches' },
      { href: '/domains', label: 'Domains' },
      { href: '/leaderboard', label: 'Leaderboard' },
    ],
  },
  {
    title: 'For Organizations',
    links: [
      { href: '/register?role=org', label: 'Post an Internship' },
      { href: '/org', label: 'Organization Dashboard' },
      { href: '/pricing', label: 'Pricing' },
    ],
  },
  {
    title: 'Trust & Safety',
    links: [
      { href: '/verify', label: 'Verify a Certificate' },
      { href: '/privacy', label: 'Privacy' },
      { href: '/terms', label: 'Terms' },
    ],
  },
];

export function SiteFooter() {
  return (
    <footer className="border-t border-border">
      <div className="container grid gap-10 py-12 md:grid-cols-4">
        <div>
          <div className="flex items-center gap-2 font-bold">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <InfinityIcon className="h-5 w-5" />
            </span>
            Infinity<span className="gradient-text">Interns</span>
          </div>
          <p className="mt-4 max-w-xs text-sm text-muted-foreground">
            India&apos;s most comprehensive engineering internship platform. Discover, apply, complete, and earn verified certificates.
          </p>
        </div>
        {COLUMNS.map((col) => (
          <div key={col.title}>
            <h4 className="mb-3 text-sm font-semibold">{col.title}</h4>
            <ul className="space-y-2">
              {col.links.map((link) => (
                <li key={link.href}>
                  <Link href={link.href} className="text-sm text-muted-foreground hover:text-foreground">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="border-t border-border py-6">
        <p className="container text-center text-xs text-muted-foreground">
          © {new Date().getFullYear()} Infinity Interns™. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
