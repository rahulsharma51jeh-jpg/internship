/**
 * Engineering branch catalog (30+ branches). `slug` is the stable identifier
 * used in URLs and the database; `name` is the human-readable label.
 */
export interface EngineeringBranch {
  slug: string;
  name: string;
  shortCode: string;
}

export const ENGINEERING_BRANCHES: EngineeringBranch[] = [
  { slug: 'computer-science', name: 'Computer Science Engineering', shortCode: 'CSE' },
  { slug: 'information-technology', name: 'Information Technology', shortCode: 'IT' },
  { slug: 'ai-ml', name: 'Artificial Intelligence & Machine Learning', shortCode: 'AIML' },
  { slug: 'data-science', name: 'Data Science', shortCode: 'DS' },
  { slug: 'cyber-security', name: 'Cyber Security', shortCode: 'CYS' },
  { slug: 'cloud-computing', name: 'Cloud Computing', shortCode: 'CC' },
  { slug: 'electronics-communication', name: 'Electronics & Communication Engineering', shortCode: 'ECE' },
  { slug: 'electrical', name: 'Electrical Engineering', shortCode: 'EE' },
  { slug: 'mechanical', name: 'Mechanical Engineering', shortCode: 'ME' },
  { slug: 'civil', name: 'Civil Engineering', shortCode: 'CE' },
  { slug: 'chemical', name: 'Chemical Engineering', shortCode: 'CHE' },
  { slug: 'agricultural', name: 'Agricultural Engineering', shortCode: 'AGRI' },
  { slug: 'biotechnology', name: 'Biotechnology', shortCode: 'BT' },
  { slug: 'biomedical', name: 'Biomedical Engineering', shortCode: 'BME' },
  { slug: 'environmental', name: 'Environmental Engineering', shortCode: 'ENV' },
  { slug: 'production', name: 'Production Engineering', shortCode: 'PROD' },
  { slug: 'industrial', name: 'Industrial Engineering', shortCode: 'IE' },
  { slug: 'mechatronics', name: 'Mechatronics', shortCode: 'MTR' },
  { slug: 'automobile', name: 'Automobile Engineering', shortCode: 'AUTO' },
  { slug: 'aerospace', name: 'Aerospace Engineering', shortCode: 'AERO' },
  { slug: 'mining', name: 'Mining Engineering', shortCode: 'MIN' },
  { slug: 'petroleum', name: 'Petroleum Engineering', shortCode: 'PET' },
  { slug: 'robotics', name: 'Robotics Engineering', shortCode: 'ROB' },
  { slug: 'marine', name: 'Marine Engineering', shortCode: 'MAR' },
  { slug: 'textile', name: 'Textile Engineering', shortCode: 'TEX' },
  { slug: 'food-technology', name: 'Food Technology', shortCode: 'FT' },
  { slug: 'instrumentation', name: 'Instrumentation Engineering', shortCode: 'IN' },
  { slug: 'renewable-energy', name: 'Renewable Energy Engineering', shortCode: 'REE' },
  { slug: 'metallurgical', name: 'Metallurgical Engineering', shortCode: 'MET' },
  { slug: 'materials-science', name: 'Materials Science Engineering', shortCode: 'MSE' },
];

export const BRANCH_SLUGS = ENGINEERING_BRANCHES.map((b) => b.slug);
