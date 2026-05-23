import axios from 'axios';

export const api = axios.create({
  baseURL: '/api',
  headers: { 'X-Company-ID': 'COMPANY_1' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function setCompanyId(companyId: string) {
  api.defaults.headers['X-Company-ID'] = companyId;
}
