import type { Role } from '@/types';

export const ROLE_HIERARCHY: Record<Role, number> = {
  ADMIN: 100,
  RECRUITER: 60,
  HR: 50,
  PAYROLL_MANAGER: 40,
  EMPLOYEE: 10,
};

export function hasMinRole(userRole: Role, minRole: Role): boolean {
  return (ROLE_HIERARCHY[userRole] ?? 0) >= (ROLE_HIERARCHY[minRole] ?? 0);
}

export interface NavItem {
  to: string;
  label: string;
  icon: string;
  minRole?: Role;
}

export const NAV_ITEMS: NavItem[] = [
  { to: '/ats', label: 'ATS Dashboard', icon: '🎯', minRole: 'RECRUITER' },
  { to: '/ats/jobs', label: 'Jobs', icon: '📋', minRole: 'RECRUITER' },
  { to: '/ats/candidates', label: 'Candidates', icon: '👤', minRole: 'RECRUITER' },
  { to: '/ats/upload', label: 'Upload CV', icon: '📄', minRole: 'RECRUITER' },
  { to: '/payroll', label: 'Payroll', icon: '💰', minRole: 'PAYROLL_MANAGER' },
  { to: '/employees', label: 'Employees', icon: '👥', minRole: 'HR' },
  { to: '/attendance', label: 'Attendance', icon: '⏰', minRole: 'EMPLOYEE' },
  { to: '/analytics', label: 'Analytics', icon: '📊', minRole: 'HR' },
  { to: '/admin', label: 'Admin', icon: '⚙️', minRole: 'ADMIN' },
];
