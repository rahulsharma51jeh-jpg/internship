/**
 * Internship domain catalog (35+ domains). Domains are cross-branch — e.g.
 * "AI Engineering" is open to CSE, AIML, Data Science students alike.
 */
export interface InternshipDomain {
  slug: string;
  name: string;
  category: DomainCategory;
}

export enum DomainCategory {
  SOFTWARE = 'SOFTWARE',
  DESIGN = 'DESIGN',
  AI_DATA = 'AI_DATA',
  SECURITY = 'SECURITY',
  CLOUD_INFRA = 'CLOUD_INFRA',
  EMERGING_TECH = 'EMERGING_TECH',
  CORE_ENGINEERING = 'CORE_ENGINEERING',
  BUSINESS = 'BUSINESS',
}

export const INTERNSHIP_DOMAINS: InternshipDomain[] = [
  { slug: 'web-development', name: 'Web Development', category: DomainCategory.SOFTWARE },
  { slug: 'frontend-development', name: 'Frontend Development', category: DomainCategory.SOFTWARE },
  { slug: 'backend-development', name: 'Backend Development', category: DomainCategory.SOFTWARE },
  { slug: 'full-stack-development', name: 'Full Stack Development', category: DomainCategory.SOFTWARE },
  { slug: 'mobile-app-development', name: 'Mobile App Development', category: DomainCategory.SOFTWARE },
  { slug: 'ui-ux-design', name: 'UI/UX Design', category: DomainCategory.DESIGN },
  { slug: 'graphic-design', name: 'Graphic Design', category: DomainCategory.DESIGN },
  { slug: 'ai-engineering', name: 'AI Engineering', category: DomainCategory.AI_DATA },
  { slug: 'machine-learning', name: 'Machine Learning', category: DomainCategory.AI_DATA },
  { slug: 'deep-learning', name: 'Deep Learning', category: DomainCategory.AI_DATA },
  { slug: 'generative-ai', name: 'Generative AI', category: DomainCategory.AI_DATA },
  { slug: 'prompt-engineering', name: 'Prompt Engineering', category: DomainCategory.AI_DATA },
  { slug: 'data-analytics', name: 'Data Analytics', category: DomainCategory.AI_DATA },
  { slug: 'data-science', name: 'Data Science', category: DomainCategory.AI_DATA },
  { slug: 'cyber-security', name: 'Cyber Security', category: DomainCategory.SECURITY },
  { slug: 'ethical-hacking', name: 'Ethical Hacking', category: DomainCategory.SECURITY },
  { slug: 'cloud-computing', name: 'Cloud Computing', category: DomainCategory.CLOUD_INFRA },
  { slug: 'devops', name: 'DevOps', category: DomainCategory.CLOUD_INFRA },
  { slug: 'blockchain', name: 'Blockchain', category: DomainCategory.EMERGING_TECH },
  { slug: 'iot', name: 'IoT', category: DomainCategory.EMERGING_TECH },
  { slug: 'embedded-systems', name: 'Embedded Systems', category: DomainCategory.EMERGING_TECH },
  { slug: 'robotics', name: 'Robotics', category: DomainCategory.EMERGING_TECH },
  { slug: 'cad-design', name: 'CAD Design', category: DomainCategory.CORE_ENGINEERING },
  { slug: 'autocad', name: 'AutoCAD', category: DomainCategory.CORE_ENGINEERING },
  { slug: 'structural-engineering', name: 'Structural Engineering', category: DomainCategory.CORE_ENGINEERING },
  { slug: 'quantity-surveying', name: 'Quantity Surveying', category: DomainCategory.CORE_ENGINEERING },
  { slug: 'gis-remote-sensing', name: 'GIS & Remote Sensing', category: DomainCategory.CORE_ENGINEERING },
  { slug: 'renewable-energy', name: 'Renewable Energy', category: DomainCategory.CORE_ENGINEERING },
  { slug: 'industrial-automation', name: 'Industrial Automation', category: DomainCategory.CORE_ENGINEERING },
  { slug: 'digital-marketing', name: 'Digital Marketing', category: DomainCategory.BUSINESS },
  { slug: 'technical-content-writing', name: 'Technical Content Writing', category: DomainCategory.BUSINESS },
  { slug: 'research-innovation', name: 'Research & Innovation', category: DomainCategory.BUSINESS },
  { slug: 'business-analytics', name: 'Business Analytics', category: DomainCategory.BUSINESS },
  { slug: 'product-management', name: 'Product Management', category: DomainCategory.BUSINESS },
  { slug: 'startup-entrepreneurship', name: 'Startup & Entrepreneurship', category: DomainCategory.BUSINESS },
];

export const DOMAIN_SLUGS = INTERNSHIP_DOMAINS.map((d) => d.slug);
