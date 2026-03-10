'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';

interface TopNavProps {
  active?: 'dashboard' | 'operations' | 'crm' | 'hr';
}

export default function TopNav({ active }: TopNavProps) {
  const router = useRouter();
  const [user, setUser] = useState('');
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const u = localStorage.getItem('bzhub_user') || 'User';
    setUser(u);
    const d = localStorage.getItem('bzhub_dark') === '1';
    setDark(d);
    if (d) document.documentElement.classList.add('dark');
  }, []);

  function toggleDark() {
    const next = !dark;
    setDark(next);
    localStorage.setItem('bzhub_dark', next ? '1' : '0');
    document.documentElement.classList.toggle('dark', next);
  }

  function logout() {
    localStorage.removeItem('bzhub_user');
    localStorage.removeItem('bzhub_role');
    localStorage.removeItem('bzhub_token');
    router.push('/');
  }

  const navItems = [
    { href: '/dashboard', label: 'Dashboard', key: 'dashboard' },
    { href: '/operations', label: 'Operations', key: 'operations' },
    { href: '/crm', label: 'CRM', key: 'crm' },
  ];

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shadow-sm">
      <div className="flex items-center gap-6">
        <Link href="/dashboard" className="flex items-center gap-2 font-bold text-lg text-primary" style={{ color: '#6D28D9' }}>
          <span className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-white text-sm font-bold" style={{ backgroundColor: '#6D28D9' }}>
            Bz
          </span>
          BzHub
        </Link>
        <div className="flex gap-1">
          {navItems.map(item => (
            <Link
              key={item.key}
              href={item.href}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                active === item.key
                  ? 'bg-purple-50 text-purple-700'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              {item.label}
            </Link>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={toggleDark}
          className="text-gray-500 hover:text-gray-700 p-1.5 rounded-lg hover:bg-gray-100 transition-colors text-sm"
          title="Toggle dark mode"
        >
          {dark ? '☀️' : '🌙'}
        </button>
        <span className="text-sm text-gray-500">{user}</span>
        <button
          onClick={logout}
          className="text-sm text-gray-500 hover:text-red-600 px-2 py-1 rounded hover:bg-red-50 transition-colors"
        >
          Logout
        </button>
      </div>
    </nav>
  );
}
