import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/features/auth/useAuth';
import { setCompanyId } from '@/lib/axios';

export default function Topbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  const handleCompanyChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setCompanyId(e.target.value);
  };

  return (
    <header className="h-16 bg-white border-b flex items-center justify-between px-6 shrink-0">
      <div className="flex items-center gap-3">
        <select
          onChange={handleCompanyChange}
          className="text-sm border rounded-lg px-2 py-1.5 bg-gray-50"
          defaultValue="COMPANY_1"
        >
          <option value="COMPANY_1">Company 1</option>
          <option value="COMPANY_2">Company 2</option>
        </select>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-sm text-gray-600 flex items-center gap-2">
          {user?.username}
          <span className="text-xs px-1.5 py-0.5 rounded bg-blue-100 text-blue-700 font-medium">
            {user?.role}
          </span>
        </span>
        <button
          onClick={handleLogout}
          className="text-sm text-red-600 hover:text-red-800 font-medium transition-colors"
        >
          Logout
        </button>
      </div>
    </header>
  );
}
