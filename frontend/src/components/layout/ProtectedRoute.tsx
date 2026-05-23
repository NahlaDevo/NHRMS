import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/features/auth/useAuth';
import type { Role } from '@/types';
import { hasMinRole } from '@/lib/roles';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface Props {
  children: React.ReactNode;
  requiredRole?: Role;
}

export default function ProtectedRoute({ children, requiredRole }: Props) {
  const { user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) return <LoadingSpinner fullScreen />;
  if (!user) return <Navigate to="/login" state={{ from: location }} replace />;
  if (requiredRole && !hasMinRole(user.role, requiredRole)) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
}
