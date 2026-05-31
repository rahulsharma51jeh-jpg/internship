import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/** Conditionally join + de-duplicate Tailwind class names. */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export function formatINR(value?: number | null): string {
  if (value == null) return '—';
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value);
}

export function stipendRange(min?: number | null, max?: number | null): string {
  if (!min && !max) return 'Unpaid / Performance-based';
  if (min && max) return `${formatINR(min)} – ${formatINR(max)}/mo`;
  return `${formatINR(min ?? max)}/mo`;
}
