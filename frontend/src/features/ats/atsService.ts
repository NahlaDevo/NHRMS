import { api } from '@/lib/axios';
import type { Job, JobCreate, Candidate, CvUploadResult, DashboardStats } from '@/types';

export const atsService = {
  getJobs: () => api.get<Job[]>('/ats/jobs').then((r) => r.data),
  getJob: (id: number) => api.get<Job>(`/ats/jobs/${id}`).then((r) => r.data),
  createJob: (data: JobCreate) => api.post<Job>('/ats/jobs', data).then((r) => r.data),
  updateJob: (id: number, data: Partial<JobCreate>) =>
    api.put<Job>(`/ats/jobs/${id}`, data).then((r) => r.data),
  deleteJob: (id: number) => api.delete(`/ats/jobs/${id}`).then((r) => r.data),

  getCandidates: () => api.get<Candidate[]>('/ats/candidates').then((r) => r.data),
  getCandidate: (id: number) =>
    api.get<Candidate>(`/ats/candidates/${id}`).then((r) => r.data),
  updateCandidate: (id: number, data: { status?: string; score?: number }) =>
    api.put<Candidate>(`/ats/candidates/${id}`, data).then((r) => r.data),

  uploadCv: (formData: FormData) =>
    api
      .post<CvUploadResult>('/ats/candidate/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data),

  getDashboardStats: () =>
    api.get<DashboardStats>('/ats/dashboard/stats').then((r) => r.data),
};
