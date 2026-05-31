import Link from 'next/link';
import {
  ArrowRight,
  Award,
  BadgeCheck,
  BrainCircuit,
  Briefcase,
  FileCheck2,
  Rocket,
  ShieldCheck,
  Sparkles,
  Trophy,
} from 'lucide-react';
import { ENGINEERING_BRANCHES, INTERNSHIP_DOMAINS } from '@infinity/shared';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Reveal } from '@/components/reveal';
import { SiteHeader } from '@/components/site-header';
import { SiteFooter } from '@/components/site-footer';

const STATS = [
  { label: 'Engineering Branches', value: `${ENGINEERING_BRANCHES.length}+` },
  { label: 'Internship Domains', value: `${INTERNSHIP_DOMAINS.length}+` },
  { label: 'Verified Certificates', value: '100%' },
  { label: 'Built to Scale', value: '1M+ users' },
];

const FEATURES = [
  { icon: Rocket, title: 'One-Click Apply', desc: 'Apply with your resume, portfolio, LinkedIn & GitHub in a single tap.' },
  { icon: BrainCircuit, title: 'AI Career Suite', desc: 'Resume ATS analyzer, skill-gap detection, recommendations & interview simulator.' },
  { icon: Briefcase, title: 'Internship Workspace', desc: 'Tasks, project submissions, attendance, weekly reports & mentor feedback.' },
  { icon: ShieldCheck, title: 'Tamper-Proof Certificates', desc: 'SHA-256 anti-tamper hash, QR verification & a blockchain-ready trust layer.' },
  { icon: Trophy, title: 'Gamified Growth', desc: 'XP points, achievement badges, skill milestones & institution leaderboards.' },
  { icon: BadgeCheck, title: 'Verified Organizations', desc: 'Admin-approved internships and a transparent multi-stage review workflow.' },
];

const WORKFLOW = [
  { step: '01', title: 'Apply', desc: 'Discover and apply to internships across every engineering branch.' },
  { step: '02', title: 'Get Selected', desc: 'Admin → organization review, then selection and onboarding.' },
  { step: '03', title: 'Complete', desc: 'Finish tasks, log attendance & submit weekly reports in your workspace.' },
  { step: '04', title: 'Get Certified', desc: 'Earn a verified, QR-checkable completion certificate for your portfolio.' },
];

export default function HomePage() {
  return (
    <>
      <SiteHeader />
      <main>
        {/* ── Hero ───────────────────────────────────────────────── */}
        <section className="relative overflow-hidden">
          <div className="pointer-events-none absolute inset-0 bg-grid-pattern bg-[size:40px_40px] opacity-50 [mask-image:radial-gradient(ellipse_at_center,black,transparent_75%)]" />
          <div className="container relative py-24 text-center md:py-32">
            <Reveal className="flex justify-center">
              <Badge className="mb-6 gap-1.5 px-4 py-1.5 text-sm">
                <Sparkles className="h-3.5 w-3.5" /> India&apos;s most comprehensive internship platform
              </Badge>
            </Reveal>
            <Reveal delay={0.05}>
              <h1 className="mx-auto max-w-4xl text-4xl font-extrabold leading-tight tracking-tight md:text-6xl">
                Where engineering students <span className="gradient-text">launch their careers</span>
              </h1>
            </Reveal>
            <Reveal delay={0.1}>
              <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
                Discover, apply, track, and complete internships across 30+ branches and 35+ domains — then earn
                certified, tamper-proof credentials that employers trust.
              </p>
            </Reveal>
            <Reveal delay={0.15}>
              <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
                <Link href="/internships">
                  <Button size="lg" className="w-full sm:w-auto">
                    Explore Internships <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
                <Link href="/register?role=org">
                  <Button size="lg" variant="outline" className="w-full sm:w-auto">
                    Post an Internship
                  </Button>
                </Link>
              </div>
            </Reveal>
          </div>
        </section>

        {/* ── Stats ──────────────────────────────────────────────── */}
        <section className="border-y border-border bg-secondary/30">
          <div className="container grid grid-cols-2 gap-8 py-12 md:grid-cols-4">
            {STATS.map((stat, i) => (
              <Reveal key={stat.label} delay={i * 0.05} className="text-center">
                <div className="text-3xl font-extrabold gradient-text md:text-4xl">{stat.value}</div>
                <div className="mt-1 text-sm text-muted-foreground">{stat.label}</div>
              </Reveal>
            ))}
          </div>
        </section>

        {/* ── Features ───────────────────────────────────────────── */}
        <section className="container py-24">
          <Reveal className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold md:text-4xl">A complete internship ecosystem</h2>
            <p className="mt-4 text-muted-foreground">
              Everything students, organizations, mentors and institutions need — in one platform.
            </p>
          </Reveal>
          <div className="mt-14 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map((feature, i) => (
              <Reveal key={feature.title} delay={(i % 3) * 0.06}>
                <Card className="h-full transition-shadow hover:shadow-lg">
                  <CardContent className="pt-6">
                    <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
                      <feature.icon className="h-6 w-6" />
                    </div>
                    <h3 className="text-lg font-semibold">{feature.title}</h3>
                    <p className="mt-2 text-sm text-muted-foreground">{feature.desc}</p>
                  </CardContent>
                </Card>
              </Reveal>
            ))}
          </div>
        </section>

        {/* ── Workflow ───────────────────────────────────────────── */}
        <section className="border-y border-border bg-secondary/30 py-24">
          <div className="container">
            <Reveal className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-bold md:text-4xl">From application to certificate</h2>
              <p className="mt-4 text-muted-foreground">A transparent, multi-stage workflow with full status tracking.</p>
            </Reveal>
            <div className="mt-14 grid gap-6 md:grid-cols-4">
              {WORKFLOW.map((item, i) => (
                <Reveal key={item.step} delay={i * 0.08}>
                  <div className="relative rounded-lg border border-border bg-card p-6">
                    <span className="text-4xl font-extrabold text-primary/20">{item.step}</span>
                    <h3 className="mt-2 text-lg font-semibold">{item.title}</h3>
                    <p className="mt-2 text-sm text-muted-foreground">{item.desc}</p>
                  </div>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        {/* ── Branches ───────────────────────────────────────────── */}
        <section className="container py-24">
          <Reveal className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold md:text-4xl">Built for every engineering branch</h2>
            <p className="mt-4 text-muted-foreground">{ENGINEERING_BRANCHES.length}+ disciplines, from CSE to Metallurgy.</p>
          </Reveal>
          <div className="mt-12 flex flex-wrap justify-center gap-3">
            {ENGINEERING_BRANCHES.map((branch, i) => (
              <Reveal key={branch.slug} delay={Math.min(i * 0.015, 0.4)}>
                <Link href={`/internships?branch=${branch.slug}`}>
                  <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-card px-4 py-2 text-sm transition-colors hover:border-primary hover:text-primary">
                    <span className="text-xs font-bold text-primary">{branch.shortCode}</span>
                    {branch.name}
                  </span>
                </Link>
              </Reveal>
            ))}
          </div>
        </section>

        {/* ── Domains ────────────────────────────────────────────── */}
        <section className="border-t border-border bg-secondary/30 py-24">
          <div className="container">
            <Reveal className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-bold md:text-4xl">{INTERNSHIP_DOMAINS.length}+ in-demand domains</h2>
              <p className="mt-4 text-muted-foreground">From Web Dev and Generative AI to CAD, GIS and Renewable Energy.</p>
            </Reveal>
            <div className="mt-12 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
              {INTERNSHIP_DOMAINS.map((domain, i) => (
                <Reveal key={domain.slug} delay={Math.min(i * 0.01, 0.3)}>
                  <Link
                    href={`/internships?domain=${domain.slug}`}
                    className="flex items-center justify-between rounded-lg border border-border bg-card px-4 py-3 text-sm font-medium transition-colors hover:border-primary hover:text-primary"
                  >
                    {domain.name}
                    <ArrowRight className="h-4 w-4 opacity-40" />
                  </Link>
                </Reveal>
              ))}
            </div>
          </div>
        </section>

        {/* ── CTA ────────────────────────────────────────────────── */}
        <section className="container py-24">
          <Reveal>
            <div className="relative overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-primary/10 via-accent/10 to-transparent p-10 text-center md:p-16">
              <Award className="mx-auto mb-4 h-12 w-12 text-primary" />
              <h2 className="text-3xl font-bold md:text-4xl">Ready to launch your career?</h2>
              <p className="mx-auto mt-4 max-w-xl text-muted-foreground">
                Join thousands of engineering students building verifiable portfolios with Infinity Interns.
              </p>
              <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
                <Link href="/register">
                  <Button size="lg">
                    Create free account <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
                <Link href="/verify">
                  <Button size="lg" variant="outline">
                    <FileCheck2 className="h-4 w-4" /> Verify a certificate
                  </Button>
                </Link>
              </div>
            </div>
          </Reveal>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
