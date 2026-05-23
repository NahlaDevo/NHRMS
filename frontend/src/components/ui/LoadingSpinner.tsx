interface Props {
  fullScreen?: boolean;
  message?: string;
}

export default function LoadingSpinner({ fullScreen, message }: Props) {
  const content = (
    <div className="flex flex-col items-center justify-center gap-3">
      <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
      {message && <p className="text-sm text-gray-500">{message}</p>}
    </div>
  );

  if (fullScreen) {
    return <div className="min-h-screen flex items-center justify-center">{content}</div>;
  }
  return <div className="flex items-center justify-center py-12">{content}</div>;
}
