import { useQuery } from '@tanstack/react-query';
import { atsService } from './atsService';
import StatCard from '@/components/ui/StatCard';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

export default function ATSDashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['ats-dashboard'],
    queryFn: atsService.getDashboardStats,
    refetchInterval: 30_000,
  });

  if (isLoading) return <LoadingSpinner message="Loading dashboard..." />;

  return (
    <div>
      <h2 className="text-xl font-bold mb-6">ATS Dashboard</h2>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Jobs" value={stats?.total_jobs ?? 0} />
        <StatCard label="Open Jobs" value={stats?.open_jobs ?? 0} color="text-green-600" />
        <StatCard label="Total Candidates" value={stats?.total_candidates ?? 0} />
        <StatCard
          label="Average Score"
          value={stats?.avg_score ? `${stats.avg_score}%` : '-'}
          color={stats?.avg_score && stats.avg_score >= 60 ? 'text-green-600' : 'text-yellow-600'}
        />
      </div>

      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h3 className="font-semibold mb-4">Candidate Pipeline</h3>
        {stats?.status_breakdown && Object.keys(stats.status_breakdown).length > 0 ? (
          <div className="space-y-3">
            {Object.entries(stats.status_breakdown).map(([status, count]) => (
              <div key={status} className="flex items-center gap-3">
                <span className="text-sm w-24 capitalize text-gray-600">{status}</span>
                <div className="flex-1 bg-gray-100 rounded-full h-2.5">
                  <div
                    className="h-2.5 rounded-full bg-blue-500 transition-all"
                    style={{
                      width: `${((count / stats.total_candidates) * 100).toFixed(1)}%`,
                    }}
                  />
                </div>
                <span className="text-sm font-medium w-8 text-right">{count}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-400">No candidates yet. Upload a CV to get started.</p>
        )}
      </div>
    </div>
  );
}
