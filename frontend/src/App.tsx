import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/features/auth/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/layout/ProtectedRoute';
import LoginPage from '@/features/auth/LoginPage';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { lazy, Suspense } from 'react';
import type { Role } from '@/types';

const ATSDashboard = lazy(() => import('@/features/ats/ATSDashboard'));
const PayrollDashboard = lazy(() => import('@/features/payroll/PayrollDashboard'));

function LazyPage({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<LoadingSpinner />}>{children}</Suspense>;
}

function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <h2 className="text-4xl font-bold text-gray-300">404</h2>
      <p className="text-gray-500 mt-2">Page not found</p>
    </div>
  );
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Navigate to="/ats" replace />} />
              <Route
                path="ats"
                element={
                  <LazyPage>
                    <ATSDashboard />
                  </LazyPage>
                }
              />
              <Route
                path="payroll"
                element={
                  <ProtectedRoute requiredRole={'PAYROLL_MANAGER' as Role}>
                    <LazyPage>
                      <PayrollDashboard />
                    </LazyPage>
                  </ProtectedRoute>
                }
              />
              <Route path="*" element={<NotFound />} />
            </Route>
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
