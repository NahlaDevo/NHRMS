import { NavLink } from 'react-router-dom';
import { useAuth } from '@/features/auth/useAuth';
import { NAV_ITEMS, hasMinRole } from '@/lib/roles';

export default function Sidebar() {
  const { user } = useAuth();
  const visibleItems = NAV_ITEMS.filter(
    (item) => user && hasMinRole(user.role, item.minRole ?? 'EMPLOYEE'),
  );

  return (
    <aside className="w-64 bg-white border-r shadow-sm flex flex-col">
      <div className="p-4 border-b">
        <h1 className="text-lg font-bold text-gray-800">HR SaaS</h1>
      </div>
      <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
        {visibleItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/ats'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-blue-50 text-blue-700 font-medium'
                  : 'text-gray-600 hover:bg-gray-50'
              }`
            }
          >
            <span className="text-base">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="p-3 border-t text-xs text-gray-400 text-center">v1.0.0</div>
    </aside>
  );
}
