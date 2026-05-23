import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { payrollService } from './payrollService';
import StatCard from '@/components/ui/StatCard';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

export default function PayrollDashboard() {
  const now = new Date();
  const defaultMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  const [month, setMonth] = useState(defaultMonth);

  const { data: summary, isLoading } = useQuery({
    queryKey: ['payroll-summary', month],
    queryFn: () => payrollService.getSummary(month),
  });

  const { data: report } = useQuery({
    queryKey: ['payroll-report', month],
    queryFn: () => payrollService.getReport(month),
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold">Payroll Dashboard</h2>
        <div className="flex items-center gap-3">
          <input
            type="month"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className="border rounded-lg px-3 py-1.5 text-sm"
          />
          <a
            href={payrollService.exportUrl(month)}
            className="bg-green-600 text-white px-4 py-1.5 rounded-lg text-sm hover:bg-green-700 transition-colors"
            target="_blank"
            rel="noopener noreferrer"
          >
            Export XLSX
          </a>
        </div>
      </div>

      {isLoading ? (
        <LoadingSpinner />
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <StatCard label="Employees" value={summary?.total_employees ?? 0} />
            <StatCard
              label="Total Net Salary"
              value={summary ? `$${summary.total_net_salary.toLocaleString()}` : '-'}
              color="text-green-600"
            />
            <StatCard
              label="Total Overtime"
              value={summary ? `$${summary.total_overtime_pay.toLocaleString()}` : '-'}
              color="text-blue-600"
            />
            <StatCard
              label="Total Deductions"
              value={summary ? `$${summary.total_deductions.toLocaleString()}` : '-'}
              color="text-red-600"
            />
          </div>

          <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
            <div className="p-4 border-b bg-gray-50">
              <h3 className="font-semibold">Payroll Records</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-gray-600">
                  <tr>
                    <th className="text-left px-4 py-3 font-medium">Employee</th>
                    <th className="text-left px-4 py-3 font-medium">Base</th>
                    <th className="text-left px-4 py-3 font-medium">Hours</th>
                    <th className="text-left px-4 py-3 font-medium">Overtime</th>
                    <th className="text-left px-4 py-3 font-medium">Deductions</th>
                    <th className="text-left px-4 py-3 font-medium">Net</th>
                    <th className="text-left px-4 py-3 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {report?.records?.length ? (
                    report.records.map((r, i) => (
                      <tr key={i} className="hover:bg-gray-50">
                        <td className="px-4 py-3">{r.employee_name || r.employee_id}</td>
                        <td className="px-4 py-3">${r.base_salary?.toLocaleString()}</td>
                        <td className="px-4 py-3">{r.hours_worked}</td>
                        <td className="px-4 py-3 text-blue-600">+${r.overtime_pay?.toFixed(2)}</td>
                        <td className="px-4 py-3 text-red-600">-${r.deductions?.toFixed(2)}</td>
                        <td className="px-4 py-3 font-medium">${r.net_salary?.toLocaleString()}</td>
                        <td className="px-4 py-3">
                          <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700">
                            {r.status}
                          </span>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={7} className="px-4 py-8 text-center text-gray-400">
                        No payroll records for {month}. Generate payroll to see records.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
