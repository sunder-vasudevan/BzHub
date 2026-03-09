'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import TopNav from '@/components/TopNav';
import { fetchKPIs, fetchTrend } from '@/lib/api';

interface KPIs {
  today_sales: number;
  inventory_value: number;
  low_stock_count: number;
  total_items: number;
  avg_daily_sales: number;
  growth_pct: number;
  pipeline_value: number;
  conversion_rate: number;
}

interface TrendRow {
  date: string;
  total: number;
}

function KPICard({
  title,
  value,
  subtitle,
  color = '#6D28D9',
}: {
  title: string;
  value: string;
  subtitle?: string;
  color?: string;
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm p-5 flex flex-col gap-1">
      <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{title}</p>
      <p className="text-2xl font-bold" style={{ color }}>
        {value}
      </p>
      {subtitle && <p className="text-xs text-gray-400">{subtitle}</p>}
    </div>
  );
}

export default function DashboardPage() {
  const router = useRouter();
  const [kpis, setKpis] = useState<KPIs | null>(null);
  const [trend, setTrend] = useState<TrendRow[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!localStorage.getItem('bzhub_user')) {
      router.push('/');
      return;
    }
    Promise.all([fetchKPIs(), fetchTrend(14)])
      .then(([k, t]) => {
        setKpis(k);
        setTrend(t);
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [router]);

  return (
    <div className="min-h-screen bg-surface">
      <TopNav active="dashboard" />
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-500">Real-time overview of your business</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            Could not load data: {error}. Make sure the BizHub API is running.
          </div>
        )}

        {loading ? (
          <div className="text-center py-20 text-gray-400">Loading dashboard…</div>
        ) : kpis ? (
          <>
            {/* KPI Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
              <KPICard
                title="Today's Sales"
                value={`$${kpis.today_sales.toLocaleString('en-US', { minimumFractionDigits: 2 })}`}
                color="#6D28D9"
              />
              <KPICard
                title="Inventory Value"
                value={`$${kpis.inventory_value.toLocaleString('en-US', { minimumFractionDigits: 2 })}`}
                color="#0EA5E9"
              />
              <KPICard
                title="Low Stock"
                value={String(kpis.low_stock_count)}
                subtitle="items below threshold"
                color={kpis.low_stock_count > 0 ? '#EF4444' : '#10B981'}
              />
              <KPICard
                title="Pipeline Value"
                value={`$${kpis.pipeline_value.toLocaleString('en-US', { minimumFractionDigits: 2 })}`}
                color="#8B5CF6"
              />
              <KPICard
                title="Avg Daily Sales"
                value={`$${kpis.avg_daily_sales.toLocaleString('en-US', { minimumFractionDigits: 2 })}`}
                color="#F59E0B"
              />
              <KPICard
                title="Growth (7d)"
                value={`${kpis.growth_pct >= 0 ? '+' : ''}${kpis.growth_pct}%`}
                color={kpis.growth_pct >= 0 ? '#10B981' : '#EF4444'}
              />
            </div>

            {/* Sales Trend Table */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-base font-semibold text-gray-800 mb-4">Sales Trend (Last 14 Days)</h2>
              {trend.length === 0 ? (
                <p className="text-gray-400 text-sm italic">No sales data available.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-100">
                        <th className="text-left py-2 px-3 text-gray-500 font-medium">Date</th>
                        <th className="text-right py-2 px-3 text-gray-500 font-medium">Total Sales</th>
                        <th className="text-left py-2 px-3 text-gray-500 font-medium">Bar</th>
                      </tr>
                    </thead>
                    <tbody>
                      {trend.map(row => {
                        const maxTotal = Math.max(...trend.map(r => r.total), 1);
                        const pct = Math.round((row.total / maxTotal) * 100);
                        return (
                          <tr key={row.date} className="border-b border-gray-50 hover:bg-gray-50">
                            <td className="py-2 px-3 text-gray-700">{row.date}</td>
                            <td className="py-2 px-3 text-right font-medium text-gray-900">
                              ${row.total.toFixed(2)}
                            </td>
                            <td className="py-2 px-3">
                              <div className="h-2 rounded-full bg-gray-100 w-40">
                                <div
                                  className="h-2 rounded-full"
                                  style={{
                                    width: `${pct}%`,
                                    backgroundColor: '#6D28D9',
                                  }}
                                />
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        ) : null}
      </main>
    </div>
  );
}
