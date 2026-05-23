const STATUS_STYLES: Record<string, string> = {
  new: 'bg-blue-100 text-blue-700',
  review: 'bg-yellow-100 text-yellow-700',
  interview: 'bg-green-100 text-green-700',
  hired: 'bg-emerald-100 text-emerald-700',
  rejected: 'bg-red-100 text-red-700',
  scheduled: 'bg-blue-100 text-blue-700',
  completed: 'bg-green-100 text-green-700',
  cancelled: 'bg-gray-100 text-gray-600',
  open: 'bg-green-100 text-green-700',
  closed: 'bg-gray-100 text-gray-600',
};

interface Props {
  status: string;
}

export default function StatusBadge({ status }: Props) {
  const style = STATUS_STYLES[status.toLowerCase()] || 'bg-gray-100 text-gray-600';
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${style}`}>
      {status}
    </span>
  );
}
