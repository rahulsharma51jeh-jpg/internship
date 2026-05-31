import Link from 'next/link';
import type { Metadata } from 'next';
import {
  Award,
  CheckCircle2,
  Flame,
  GraduationCap,
  TrendingUp,
  Trophy,
  FileText,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { SiteHeader } from '@/components/site-header';
import { SiteFooter } from '@/components/site-footer';

export const metadata: Metadata = { title: 'Student Dashboard' };

// Representative demo data; the live dashboard is fed by GET /api/users/me/dashboard.
const DEMO = {
  name: 'Aarav Sharma',
  branch: 'Computer Science Engineering',
  profileCompletion: 70,
  xp: 250,
  level: 2,
  certificates: 1,
  badges: 3,
  pipeline: [
    { label: 'Applied', count: 5, variant: 'secondary' as const },
    { label: 'Under Review', count: 2, variant: 'warning' as const },
    { label: 'Selected', count: 1, variant: 'default' as const },
    { label: 'Ongoing', count: 1, variant: 'default' as const },
    { label: 'Completed', count: 1, variant: 'success' as const },
  ],
  recommendations: [
    { title: 'Backend Developer Intern', org: 'TechNova Labs', domain: 'Backend Development', slug: 'technova-full-stack-intern-2026' },
    { title: 'ML Research Intern', org: 'QuantML', domain: 'Machine Learning', slug: 'quantml-ml-research-intern' },
    { title: 'Cloud DevOps Intern', org: 'NimbusOps', domain: 'DevOps', slug: 'nimbusops-devops-intern' },
  ],
};

export default function DashboardPage() {
  const stats = [
    { label: 'Profile Completion', value: `${DEMO.profileCompletion}%`, icon: TrendingUp },
    { label: 'XP Points', value: DEMO.xp, icon: Flame },
    { label: 'Level', value: DEMO.level, icon: Trophy },
    { label: 'Certificates', value: DEMO.certificates, icon: Award },
  ];

  return (
    <>
      <SiteHeader />
      <main className="container py-10">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h1 className="text-2xl font-bold md:text-3xl">Welcome back, {DEMO.name.split(' ')[0]} 👋</h1>
            <p className="mt-1 flex items-center gap-1.5 text-sm text-muted-foreground">
              <GraduationCap className="h-4 w-4" /> {DEMO.branch}
            </p>
          </div>
          <Link href="/dashboard/profile">
            <Button variant="outline">Complete your profile</Button>
          </Link>
        </div>

        {/* Profile completion bar */}
        <div className="mt-6 rounded-lg border border-border bg-card p-4">
          <div className="mb-2 flex items-center justify-between text-sm">
            <span className="font-medium">Profile strength</span>
            <span className="text-muted-foreground">{DEMO.profileCompletion}%</span>
          </div>
          <div className="h-2.5 w-full overflow-hidden rounded-full bg-secondary">
            <div className="h-full rounded-full bg-primary" style={{ width: `${DEMO.profileCompletion}%` }} />
          </div>
        </div>

        {/* Stat cards */}
        <div className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
          {stats.map((s) => (
            <Card key={s.label}>
              <CardContent className="flex items-center gap-4 pt-6">
                <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <s.icon className="h-5 w-5" />
                </div>
                <div>
                  <div className="text-2xl font-bold">{s.value}</div>
                  <div className="text-xs text-muted-foreground">{s.label}</div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-3">
          {/* Application tracker */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Application Tracker</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {DEMO.pipeline.map((stage) => (
                <div key={stage.label} className="flex items-center justify-between rounded-md border border-border px-4 py-3">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium">{stage.label}</span>
                  </div>
                  <Badge variant={stage.variant}>{stage.count}</Badge>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle>Recommended for you</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {DEMO.recommendations.map((rec) => (
                <Link
                  key={rec.slug}
                  href={`/internships/${rec.slug}`}
                  className="block rounded-md border border-border p-3 transition-colors hover:border-primary"
                >
                  <div className="text-sm font-semibold">{rec.title}</div>
                  <div className="text-xs text-muted-foreground">{rec.org}</div>
                  <Badge variant="secondary" className="mt-2">
                    {rec.domain}
                  </Badge>
                </Link>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Workspace shortcut */}
        <Card className="mt-6">
          <CardContent className="flex flex-col items-center justify-between gap-4 pt-6 sm:flex-row">
            <div className="flex items-center gap-3">
              <FileText className="h-6 w-6 text-primary" />
              <div>
                <div className="font-semibold">Internship Workspace</div>
                <div className="text-sm text-muted-foreground">
                  Submit tasks, log attendance, and file weekly reports for your ongoing internship.
                </div>
              </div>
            </div>
            <Link href="/dashboard/workspace">
              <Button>Open workspace</Button>
            </Link>
          </CardContent>
        </Card>
      </main>
      <SiteFooter />
    </>
  );
}
