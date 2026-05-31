import Link from 'next/link';
import { CheckCircle2, XCircle, AlertTriangle, Calendar, Building2, GraduationCap } from 'lucide-react';
import { verifyCertificate, type VerifyResult } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { SiteHeader } from '@/components/site-header';
import { SiteFooter } from '@/components/site-footer';

export const dynamic = 'force-dynamic';

const REASON_COPY: Record<VerifyResult['reason'], string> = {
  OK: 'This certificate is authentic and was issued by Infinity Interns.',
  NOT_FOUND: 'No certificate matches this identifier. Please check and try again.',
  REVOKED: 'This certificate has been revoked by the issuing administrator.',
  TAMPERED: 'Integrity check failed — the certificate data does not match its secure hash.',
};

export default async function VerifyResultPage({ params }: { params: { id: string } }) {
  let result: VerifyResult;
  try {
    result = await verifyCertificate(params.id);
  } catch {
    result = { valid: false, reason: 'NOT_FOUND' };
  }

  const valid = result.valid;
  const cert = result.certificate;

  return (
    <>
      <SiteHeader />
      <main className="container flex flex-col items-center py-16">
        <Card className="w-full max-w-xl">
          <CardContent className="pt-8">
            <div className="flex flex-col items-center text-center">
              {valid ? (
                <CheckCircle2 className="h-16 w-16 text-emerald-500" />
              ) : result.reason === 'TAMPERED' ? (
                <AlertTriangle className="h-16 w-16 text-amber-500" />
              ) : (
                <XCircle className="h-16 w-16 text-red-500" />
              )}
              <h1 className="mt-4 text-2xl font-bold">
                {valid ? 'Verified Certificate' : 'Verification Failed'}
              </h1>
              <p className="mt-2 max-w-sm text-sm text-muted-foreground">{REASON_COPY[result.reason]}</p>
              <Badge variant={valid ? 'success' : 'danger'} className="mt-4">
                {result.reason}
              </Badge>
            </div>

            {valid && cert && (
              <div className="mt-8 space-y-4 border-t border-border pt-6">
                <Field label="Certificate ID" value={cert.certificateId} mono />
                <Field label="Awarded to" value={cert.studentName} icon={<GraduationCap className="h-4 w-4" />} />
                <Field label="Title" value={cert.title} />
                <Field label="Organization" value={cert.organizationName} icon={<Building2 className="h-4 w-4" />} />
                <Field label="Domain" value={cert.domainName} />
                {cert.grade && <Field label="Performance grade" value={cert.grade.replace('_', '+')} />}
                {cert.durationWeeks && <Field label="Duration" value={`${cert.durationWeeks} weeks`} />}
                <Field
                  label="Issued on"
                  value={new Date(cert.issueDate).toLocaleDateString('en-IN', { dateStyle: 'long' })}
                  icon={<Calendar className="h-4 w-4" />}
                />
                <Field label="Verification number" value={cert.verificationNumber} mono />
              </div>
            )}

            <div className="mt-8 flex justify-center">
              <Link href="/verify">
                <Button variant="outline">Verify another certificate</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </main>
      <SiteFooter />
    </>
  );
}

function Field({
  label,
  value,
  mono,
  icon,
}: {
  label: string;
  value: string;
  mono?: boolean;
  icon?: React.ReactNode;
}) {
  return (
    <div className="flex items-center justify-between gap-4">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className={`flex items-center gap-1.5 text-right text-sm font-medium ${mono ? 'font-mono' : ''}`}>
        {icon}
        {value}
      </span>
    </div>
  );
}
