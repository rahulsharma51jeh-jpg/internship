'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ShieldCheck, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SiteHeader } from '@/components/site-header';
import { SiteFooter } from '@/components/site-footer';

export default function VerifyLandingPage() {
  const router = useRouter();
  const [identifier, setIdentifier] = useState('');

  return (
    <>
      <SiteHeader />
      <main className="container flex min-h-[70vh] flex-col items-center justify-center py-16 text-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 text-primary">
          <ShieldCheck className="h-8 w-8" />
        </div>
        <h1 className="mt-6 text-3xl font-bold md:text-4xl">Verify a Certificate</h1>
        <p className="mt-3 max-w-md text-muted-foreground">
          Enter a Certificate ID (e.g. <code className="rounded bg-secondary px-1.5 py-0.5">INF-2026-AB12CD34</code>) or
          verification number. Each certificate is protected by an anti-tamper hash.
        </p>

        <form
          className="mt-8 flex w-full max-w-md items-center gap-2 rounded-lg border border-border bg-card px-4 py-2"
          onSubmit={(e) => {
            e.preventDefault();
            if (identifier.trim()) router.push(`/verify/${encodeURIComponent(identifier.trim())}`);
          }}
        >
          <Search className="h-5 w-5 text-muted-foreground" />
          <input
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            placeholder="Certificate ID or verification number"
            className="w-full bg-transparent py-1.5 text-sm outline-none placeholder:text-muted-foreground"
          />
          <Button type="submit" size="sm">
            Verify
          </Button>
        </form>
      </main>
      <SiteFooter />
    </>
  );
}
