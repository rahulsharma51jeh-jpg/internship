import Link from 'next/link';
import type { Metadata } from 'next';
import { Infinity as InfinityIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

export const metadata: Metadata = { title: 'Create account' };

export default function RegisterPage({ searchParams }: { searchParams: { role?: string } }) {
  const isOrg = searchParams.role === 'org';
  return (
    <main className="container flex min-h-screen flex-col items-center justify-center py-16">
      <Link href="/" className="mb-8 flex items-center gap-2 text-lg font-bold">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <InfinityIcon className="h-5 w-5" />
        </span>
        Infinity<span className="gradient-text">Interns</span>
      </Link>

      <Card className="w-full max-w-sm">
        <CardContent className="pt-6">
          <h1 className="text-xl font-bold">{isOrg ? 'Register your organization' : 'Create your account'}</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {isOrg ? 'Start posting internships and recruiting interns.' : 'Join and start applying in minutes.'}
          </p>

          {/* Posts to POST /api/auth/register */}
          <form className="mt-6 space-y-4" action="/api/auth/register" method="post">
            <input type="hidden" name="role" value={isOrg ? 'ORGANIZATION' : 'STUDENT'} />
            <div className="space-y-1.5">
              <label htmlFor="fullName" className="text-sm font-medium">
                {isOrg ? 'Contact name' : 'Full name'}
              </label>
              <input
                id="fullName"
                name="fullName"
                required
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
            {isOrg && (
              <div className="space-y-1.5">
                <label htmlFor="companyName" className="text-sm font-medium">
                  Company name
                </label>
                <input
                  id="companyName"
                  name="companyName"
                  required
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"
                />
              </div>
            )}
            <div className="space-y-1.5">
              <label htmlFor="email" className="text-sm font-medium">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
            <div className="space-y-1.5">
              <label htmlFor="password" className="text-sm font-medium">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                minLength={8}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
            <Button className="w-full" type="submit">
              Create account
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-muted-foreground">
            Already have an account?{' '}
            <Link href="/login" className="font-medium text-primary hover:underline">
              Log in
            </Link>
          </p>
        </CardContent>
      </Card>
    </main>
  );
}
