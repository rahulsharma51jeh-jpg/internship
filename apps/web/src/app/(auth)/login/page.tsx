import Link from 'next/link';
import type { Metadata } from 'next';
import { Infinity as InfinityIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

export const metadata: Metadata = { title: 'Log in' };

export default function LoginPage() {
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
          <h1 className="text-xl font-bold">Welcome back</h1>
          <p className="mt-1 text-sm text-muted-foreground">Log in to your account to continue.</p>

          {/* Posts to POST /api/auth/login — wire up with a client action in production. */}
          <form className="mt-6 space-y-4" action="/api/auth/login" method="post">
            <div className="space-y-1.5">
              <label htmlFor="email" className="text-sm font-medium">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                defaultValue="student@example.com"
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
                defaultValue="Password@123"
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
            <Button className="w-full" type="submit">
              Log in
            </Button>
          </form>

          <div className="mt-4 flex flex-col gap-2">
            <Button variant="outline" className="w-full">
              Continue with Google
            </Button>
            <Button variant="outline" className="w-full">
              Continue with LinkedIn
            </Button>
          </div>

          <p className="mt-6 text-center text-sm text-muted-foreground">
            New here?{' '}
            <Link href="/register" className="font-medium text-primary hover:underline">
              Create an account
            </Link>
          </p>
        </CardContent>
      </Card>
    </main>
  );
}
