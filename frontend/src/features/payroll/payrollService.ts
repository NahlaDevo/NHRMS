import { api } from '@/lib/axios';
import type { PayrollRecord, PayrollSummary } from '@/types';

export const payrollService = {
  getReport: (month: string) =>
    api.get<{ month: string; records: PayrollRecord[] }>(`/payroll/report/${month}`).then((r) => r.data),

  getSummary: (month: string) =>
    api.get<PayrollSummary>(`/payroll/summary/${month}`).then((r) => r.data),

  getEmployeePayroll: (employeeId: string) =>
    api
      .get<{ employee_id: string; records: PayrollRecord[] }>(`/payroll/${employeeId}`)
      .then((r) => r.data),

  generatePayroll: (employeeId: string, month: string) =>
    api.get(`/payroll/generate/${employeeId}/${month}`).then((r) => r.data),

  generateAll: (month: string) =>
    api.post(`/payroll/generate-all/${month}`).then((r) => r.data),

  exportUrl: (month: string) => `/api/payroll/export/${month}`,
};
