import { createHash, createSign, generateKeyPairSync } from 'crypto';

/**
 * Canonical fields that uniquely & immutably describe a certificate. Hashing a
 * stable serialization of these gives us an anti-tamper fingerprint: change any
 * field after issue and verification fails.
 */
export interface CertificateContent {
  certificateId: string;
  studentName: string;
  organizationName: string;
  domainName: string;
  title: string;
  durationWeeks?: number | null;
  startDate?: string | null;
  endDate?: string | null;
  grade?: string | null;
  issueDate: string;
}

/** Deterministic, key-sorted serialization so the hash is reproducible. */
export function canonicalize(content: CertificateContent): string {
  const ordered = Object.keys(content)
    .sort()
    .reduce<Record<string, unknown>>((acc, key) => {
      acc[key] = (content as unknown as Record<string, unknown>)[key] ?? null;
      return acc;
    }, {});
  return JSON.stringify(ordered);
}

/** SHA-256 anti-tamper hash of the canonical content. */
export function hashContent(content: CertificateContent): string {
  return createHash('sha256').update(canonicalize(content)).digest('hex');
}

/**
 * Sign the content hash with an RSA private key (PEM). Returns base64 signature.
 * If no key is configured we return null (dev mode) — verification still works
 * via the SHA-256 hash; the signature is an additional, optional trust layer.
 */
export function signHash(hash: string, privateKeyPem?: string): string | null {
  if (!privateKeyPem) return null;
  const signer = createSign('RSA-SHA256');
  signer.update(hash);
  signer.end();
  return signer.sign(privateKeyPem, 'base64');
}

/** Helper to mint a dev keypair (used in tests / first-run). */
export function generateSigningKeyPair() {
  return generateKeyPairSync('rsa', {
    modulusLength: 2048,
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' },
  });
}
