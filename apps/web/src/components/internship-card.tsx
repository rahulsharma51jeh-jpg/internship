import Link from 'next/link';
import { Building2, Clock, MapPin, Users, BadgeCheck } from 'lucide-react';
import type { InternshipCard as InternshipCardType } from '@/lib/api';
import { Card, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { stipendRange } from '@/lib/utils';

export function InternshipCard({ internship }: { internship: InternshipCardType }) {
  return (
    <Card className="flex h-full flex-col transition-shadow hover:shadow-lg">
      <CardContent className="flex-1 pt-6">
        <div className="mb-3 flex items-center justify-between">
          <Badge variant="secondary">{internship.domain.name}</Badge>
          <Badge variant={internship.workMode === 'REMOTE' ? 'success' : 'outline'}>{internship.workMode}</Badge>
        </div>
        <h3 className="text-lg font-semibold leading-snug">{internship.title}</h3>
        <div className="mt-2 flex items-center gap-1.5 text-sm text-muted-foreground">
          <Building2 className="h-4 w-4" />
          {internship.organization.companyName}
          {internship.organization.verified && <BadgeCheck className="h-4 w-4 text-primary" />}
        </div>

        <div className="mt-4 grid grid-cols-2 gap-2 text-sm text-muted-foreground">
          <span className="flex items-center gap-1.5">
            <Clock className="h-4 w-4" /> {internship.durationWeeks} weeks
          </span>
          <span className="flex items-center gap-1.5">
            <MapPin className="h-4 w-4" /> {internship.branch?.shortCode ?? 'All branches'}
          </span>
          <span className="col-span-2 flex items-center gap-1.5 font-medium text-foreground">
            {stipendRange(internship.stipendMin, internship.stipendMax)}
          </span>
        </div>
      </CardContent>
      <CardFooter className="justify-between">
        <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <Users className="h-3.5 w-3.5" /> {internship._count?.applications ?? 0} applicants
        </span>
        <Link href={`/internships/${internship.slug}`}>
          <Button size="sm" variant="outline">
            View &amp; Apply
          </Button>
        </Link>
      </CardFooter>
    </Card>
  );
}
