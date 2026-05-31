/* eslint-disable no-console */
import { PrismaClient, DomainCategory, UserRole, AccountStatus } from '@prisma/client';
import * as argon2 from 'argon2';

// Imported from the shared package (relative path keeps ts-node happy without path aliases).
import { ENGINEERING_BRANCHES } from '../../../packages/shared/src/branches';
import { INTERNSHIP_DOMAINS } from '../../../packages/shared/src/domains';

const prisma = new PrismaClient();

const SKILLS = [
  'JavaScript', 'TypeScript', 'React', 'Next.js', 'Node.js', 'NestJS', 'Python',
  'Django', 'Flask', 'SQL', 'PostgreSQL', 'MongoDB', 'Docker', 'Kubernetes',
  'AWS', 'TensorFlow', 'PyTorch', 'Pandas', 'Figma', 'Solidity', 'C++', 'Rust',
  'Go', 'AutoCAD', 'SolidWorks', 'MATLAB', 'Linux', 'Git', 'GraphQL', 'Redis',
];

const BADGES = [
  { slug: 'first-application', name: 'First Steps', description: 'Submitted your first application', xpReward: 50 },
  { slug: 'first-internship', name: 'Intern Initiate', description: 'Started your first internship', xpReward: 200 },
  { slug: 'certified', name: 'Certified Pro', description: 'Earned your first certificate', xpReward: 300 },
  { slug: 'perfect-attendance', name: 'Always On', description: '100% attendance in an internship', xpReward: 150 },
  { slug: 'skill-master', name: 'Skill Master', description: 'Verified 10+ skills', xpReward: 250 },
];

function slugify(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

async function seedTaxonomy() {
  console.log('→ Seeding branches...');
  for (const branch of ENGINEERING_BRANCHES) {
    await prisma.branch.upsert({
      where: { slug: branch.slug },
      update: { name: branch.name, shortCode: branch.shortCode },
      create: { slug: branch.slug, name: branch.name, shortCode: branch.shortCode },
    });
  }

  console.log('→ Seeding domains...');
  for (const domain of INTERNSHIP_DOMAINS) {
    await prisma.domain.upsert({
      where: { slug: domain.slug },
      update: { name: domain.name, category: domain.category as DomainCategory },
      create: { slug: domain.slug, name: domain.name, category: domain.category as DomainCategory },
    });
  }

  console.log('→ Seeding skills...');
  for (const name of SKILLS) {
    const slug = slugify(name);
    await prisma.skill.upsert({ where: { slug }, update: { name }, create: { slug, name } });
  }

  console.log('→ Seeding badges...');
  for (const badge of BADGES) {
    await prisma.badge.upsert({ where: { slug: badge.slug }, update: badge, create: badge });
  }
}

async function seedUsers() {
  console.log('→ Seeding demo users...');
  const password = await argon2.hash('Password@123');

  // Admin
  await prisma.user.upsert({
    where: { email: 'admin@infinityinterns.com' },
    update: {},
    create: {
      email: 'admin@infinityinterns.com',
      passwordHash: password,
      fullName: 'Platform Admin',
      roles: [UserRole.ADMIN, UserRole.SUPER_ADMIN],
      status: AccountStatus.ACTIVE,
      emailVerified: true,
    },
  });

  // Organization
  const org = await prisma.user.upsert({
    where: { email: 'hr@technova.com' },
    update: {},
    create: {
      email: 'hr@technova.com',
      passwordHash: password,
      fullName: 'TechNova HR',
      roles: [UserRole.ORGANIZATION],
      status: AccountStatus.ACTIVE,
      emailVerified: true,
      organizationProfile: {
        create: {
          companyName: 'TechNova Labs',
          industry: 'Software',
          city: 'Bengaluru',
          state: 'Karnataka',
          about: 'Building developer tools for the next billion engineers.',
          verified: true,
        },
      },
    },
    include: { organizationProfile: true },
  });

  // Student
  const cse = await prisma.branch.findUnique({ where: { slug: 'computer-science' } });
  const student = await prisma.user.upsert({
    where: { email: 'student@example.com' },
    update: {},
    create: {
      email: 'student@example.com',
      passwordHash: password,
      fullName: 'Aarav Sharma',
      roles: [UserRole.STUDENT],
      status: AccountStatus.ACTIVE,
      emailVerified: true,
      studentProfile: {
        create: {
          branchId: cse?.id,
          collegeName: 'IIT Delhi',
          graduationYear: 2027,
          cgpa: 8.6,
          city: 'New Delhi',
          state: 'Delhi',
          profileCompletion: 70,
          xpPoints: 250,
          level: 2,
        },
      },
    },
    include: { studentProfile: true },
  });

  // A sample published internship
  const domain = await prisma.domain.findUnique({ where: { slug: 'full-stack-development' } });
  if (org.organizationProfile && domain) {
    await prisma.internship.upsert({
      where: { slug: 'technova-full-stack-intern-2026' },
      update: {},
      create: {
        slug: 'technova-full-stack-intern-2026',
        title: 'Full Stack Developer Intern',
        description: 'Work on production React/NestJS apps alongside senior engineers.',
        responsibilities: 'Build features, write tests, ship to production weekly.',
        eligibility: 'CSE/IT, 2026-2027 graduates, strong JS fundamentals.',
        organizationId: org.organizationProfile.id,
        branchId: cse?.id,
        domainId: domain.id,
        workMode: 'REMOTE',
        stipendMin: 15000,
        stipendMax: 25000,
        durationWeeks: 12,
        openings: 3,
        status: 'OPEN',
        approvedAt: new Date(),
      },
    });
  }

  console.log(`   admin@infinityinterns.com / student@example.com / hr@technova.com  (password: Password@123)`);
  void student;
}

async function main() {
  await seedTaxonomy();
  await seedUsers();
  console.log('✅ Seed complete.');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
