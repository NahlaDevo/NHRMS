interface Props {
  label: string;
  value: string | number;
  color?: string;
}

export default function StatCard({ label, value, color = 'text-gray-900' }: Props) {
  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border">
      <div className="text-sm text-gray-500">{label}</div>
      <div className={`text-2xl font-bold mt-1 ${color}`}>{value}</div>
    </div>
  );
}
