import Link from 'next/link';
import { Search } from 'lucide-react';
import type { Metadata } from 'next';
import { INTERNSHIP_DOMAINS, ENGINEERING_BRANCHES } from '@infinity/shared';
import { getInternships, type InternshipCard as InternshipCardType } from '@/lib/api';
import { SAMPLE_INTERNSHIPS } from '@/lib/sample-data';
import { InternshipCard } from '@/components/internship-card';
import { Badge } from '@/components/ui/badge';
import { SiteHeader } from '@/components/site-header';
import { SiteFooter } from '@/components/site-footer';

export const metadata: Metadata = {
  title: 'Browse Internships',
  description: 'Search live internships across every engineering branch and technology domain.',
};

export const dynamic = 'force-dynamic';

interface SearchParams {
  domain?: string;
  branch?: string;
  workMode?: string;
  q?: string;
}

export default async function InternshipsPage({ searchParams }: { searchParams: SearchParams }) {
  let internships: InternshipCardType[] = [];
  let total = 0;
  let usedFallback = false;

  try {
    const result = await getInternships({
      domain: searchParams.domain,
      branch: searchParams.branch,
      workMode: searchParams.workMode,
      q: searchParams.q,
      limit: 24,
    });
    internships = result.items;
    total = result.meta.total;
  } catch {
    // API not reachable — show representative sample data so the UI still renders.
    usedFallback = true;
    internships = SAMPLE_INTERNSHIPS.filter(
      (i) =>
        (!searchParams.domain || i.domain.slug === searchParams.domain) &&
        (!searchParams.workMode || i.workMode === searchParams.workMode),
    );
    total = internships.length;
  }

  return (
    <>
      <SiteHeader />
      <main className="container py-12">
        <div className="mb-8">
          <h1 className="text-3xl font-bold md:text-4xl">Internships</h1>
          <p className="mt-2 text-muted-foreground">
            {total} opportunit{total === 1 ? 'y' : 'ies'} across {ENGINEERING_BRANCHES.length}+ branches and{' '}
            {INTERNSHIP_DOMAINS.length}+ domains.
          </p>
        </div>

        {/* Search */}
        <form action="/internships" className="mb-6 flex items-center gap-2 rounded-lg border border-border bg-card px-4 py-2">
          <Search className="h-5 w-5 text-muted-foreground" />
          <input
            name="q"
            defaultValue={searchParams.q}
            placeholder="Search by role, skill or keyword…"
            className="w-full bg-transparent py-1.5 text-sm outline-none placeholder:text-muted-foreground"
          />
        </form>

        {/* Domain filter chips */}
        <div className="mb-8 flex flex-wrap gap-2">
          <Link href="/internships">
            <Badge variant={!searchParams.domain ? 'default' : 'outline'}>All</Badge>
          </Link>
          {INTERNSHIP_DOMAINS.slice(0, 16).map((d) => (
            <Link key={d.slug} href={`/internships?domain=${d.slug}`}>
              <Badge variant={searchParams.domain === d.slug ? 'default' : 'outline'}>{d.name}</Badge>
            </Link>
          ))}
        </div>

        {usedFallback && (
          <div className="mb-6 rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-700 dark:text-amber-300">
            Showing sample data — start the API (<code>pnpm api:dev</code>) and seed the database to see live listings.
          </div>
        )}

        {internships.length === 0 ? (
          <div className="rounded-lg border border-dashed border-border py-20 text-center text-muted-foreground">
            No internships match your filters yet.
          </div>
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {internships.map((internship) => (
              <InternshipCard key={internship.id} internship={internship} />
            ))}
          </div>
        )}
      </main>
      <SiteFooter />
    </>
  );
}
