/**
 * Thin typed fetch wrapper around the Infinity Interns API.
 *
 * The API wraps every response in `{ success, data }`; this client unwraps it
 * and throws a typed error on failure. An access token (when present) is sent
 * as a Bearer header.
 */
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:4000';

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
  }
}

interface ApiEnvelope<T> {
  success: boolean;
  data: T;
  message?: string | string[];
}

export interface RequestOptions extends RequestInit {
  token?: string;
  /** Next.js fetch caching controls. */
  revalidate?: number;
}

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { token, revalidate, headers, ...rest } = options;

  const res = await fetch(`${API_BASE}/api${path}`, {
    ...rest,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    ...(revalidate !== undefined ? { next: { revalidate } } : {}),
  });

  const body = (await res.json().catch(() => null)) as ApiEnvelope<T> | null;

  if (!res.ok || !body?.success) {
    const msg = body?.message
      ? Array.isArray(body.message)
        ? body.message.join(', ')
        : body.message
      : `Request failed (${res.status})`;
    throw new ApiError(msg, res.status);
  }

  return body.data;
}

// ── Typed helpers for the public surface used by server components ──────────────

export interface InternshipCard {
  id: string;
  slug: string;
  title: string;
  workMode: 'REMOTE' | 'ONSITE' | 'HYBRID';
  stipendMin?: number | null;
  stipendMax?: number | null;
  durationWeeks: number;
  organization: { companyName: string; logoUrl?: string | null; verified?: boolean };
  domain: { name: string; slug: string };
  branch?: { name: string; shortCode: string } | null;
  _count?: { applications: number };
}

export interface Paginated<T> {
  items: T[];
  meta: { page: number; limit: number; total: number; totalPages: number };
}

export function getInternships(params: Record<string, string | number | undefined> = {}) {
  const query = new URLSearchParams(
    Object.entries(params)
      .filter(([, v]) => v !== undefined && v !== '')
      .map(([k, v]) => [k, String(v)]),
  ).toString();
  return apiFetch<Paginated<InternshipCard>>(`/internships${query ? `?${query}` : ''}`, { revalidate: 30 });
}

export interface VerifyResult {
  valid: boolean;
  reason: 'OK' | 'NOT_FOUND' | 'REVOKED' | 'TAMPERED';
  certificate?: {
    certificateId: string;
    studentName: string;
    organizationName: string;
    domainName: string;
    title: string;
    grade?: string | null;
    durationWeeks?: number | null;
    issueDate: string;
    verificationNumber: string;
  };
}

export function verifyCertificate(identifier: string) {
  return apiFetch<VerifyResult>(`/certificates/verify/${encodeURIComponent(identifier)}`);
}
