/**
 * Platform actor roles. A single account can theoretically carry more than one
 * role (e.g. a mentor who is also an admin) — roles are stored as an array.
 */
export enum UserRole {
  STUDENT = 'STUDENT',
  ORGANIZATION = 'ORGANIZATION',
  MENTOR = 'MENTOR',
  INSTITUTION = 'INSTITUTION',
  ADMIN = 'ADMIN',
  SUPER_ADMIN = 'SUPER_ADMIN',
}

export const ALL_ROLES = Object.values(UserRole);
