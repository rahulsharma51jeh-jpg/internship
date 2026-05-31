/**
 * Centralized, typed configuration loaded from environment variables.
 * Registered via `ConfigModule.forRoot({ load: [configuration] })`.
 */
export default () => ({
  env: process.env.NODE_ENV ?? 'development',
  port: parseInt(process.env.API_PORT ?? '4000', 10),
  webUrl: process.env.WEB_URL ?? 'http://localhost:3000',

  database: {
    url: process.env.DATABASE_URL,
  },

  redis: {
    url: process.env.REDIS_URL ?? 'redis://localhost:6379',
  },

  jwt: {
    accessSecret: process.env.JWT_ACCESS_SECRET ?? 'dev-access-secret',
    accessTtl: process.env.JWT_ACCESS_TTL ?? '15m',
    refreshSecret: process.env.JWT_REFRESH_SECRET ?? 'dev-refresh-secret',
    refreshTtl: process.env.JWT_REFRESH_TTL ?? '7d',
  },

  storage: {
    provider: process.env.STORAGE_PROVIDER ?? 'local',
    bucket: process.env.STORAGE_BUCKET ?? 'infinity-interns',
    region: process.env.STORAGE_REGION ?? 'ap-south-1',
    endpoint: process.env.STORAGE_ENDPOINT,
  },

  certificates: {
    verifyBaseUrl: process.env.CERT_VERIFY_BASE_URL ?? 'http://localhost:3000/verify',
    signingKey: process.env.CERT_SIGNING_PRIVATE_KEY,
  },
});
