// ── Auth ──
export interface User {
  username: string;
  role: Role;
  user_id: string;
}

export type Role = 'ADMIN' | 'RECRUITER' | 'HR' | 'PAYROLL_MANAGER' | 'EMPLOYEE';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  username: string;
  role: Role;
  refresh_token: string;
}

// ── Jobs ──
export interface Job {
  id: number;
  title: string;
  department: string;
  description: string;
  requirements: string;
  keywords: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface JobCreate {
  title: string;
  department?: string;
  description?: string;
  requirements?: string;
  keywords?: string;
  status?: string;
}

// ── Candidates ──
export interface Candidate {
  id: number;
  name: string;
  email: string;
  phone: string;
  cv_filename: string;
  score: number;
  status: string;
  skills: string;
  experience_years: number;
  job_id: number | null;
  created_at: string;
}

export interface CvUploadResult {
  candidate: Candidate;
  score_result: ScoreResult;
}

export interface ScoreResult {
  score: number;
  skills: string[];
  experience_years: number;
  tech_skills_match: number;
  keywords_match: number;
}

// ── Interviews ──
export interface Interview {
  id: number;
  candidate_id: number;
  job_id: number;
  scheduled_time: string;
  duration_minutes: number;
  status: string;
  notes: string;
  candidate_name: string;
  job_title: string;
}

export interface InterviewCreate {
  candidate_id: number;
  job_id: number;
  scheduled_time: string;
  duration_minutes?: number;
  notes?: string;
}

// ── Payroll ──
export interface PayrollRecord {
  employee_id: string;
  employee_name: string;
  month: string;
  base_salary: number;
  hours_worked: number;
  overtime_hours: number;
  overtime_pay: number;
  deductions: number;
  net_salary: number;
  status: string;
}

export interface PayrollSummary {
  month: string;
  total_employees: number;
  total_net_salary: number;
  total_overtime_pay: number;
  total_deductions: number;
  average_salary: number;
}

// ── Dashboard ──
export interface DashboardStats {
  total_jobs: number;
  open_jobs: number;
  total_candidates: number;
  avg_score: number;
  status_breakdown: Record<string, number>;
  scheduled_interviews: number;
}
