"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import AppLayout from "@/components/layout/AppLayout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { fetchKPIs, fetchTrend } from "@/lib/api"
import {
  DollarSign,
  Package,
  AlertTriangle,
  Users,
  TrendingUp,
  BarChart3,
} from "lucide-react"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"
import { useCurrency } from "@/hooks/useCurrency"

interface KPIs {
  today_sales: number
  inventory_value: number
  low_stock_count: number
  total_items: number
  avg_daily_sales: number
  growth_pct: number
  pipeline_value: number
  conversion_rate: number
}

interface TrendRow {
  date: string
  total: number
}

interface KPICardProps {
  title: string
  value: string
  subtitle?: string
  trend?: string
  trendUp?: boolean
  trendHref?: string
  icon: React.ReactNode
  iconBg: string
}

function KPICard({ title, value, subtitle, trend, trendUp, trendHref, icon, iconBg }: KPICardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <div
          className="h-9 w-9 rounded-lg flex items-center justify-center flex-shrink-0"
          style={{ backgroundColor: iconBg + "20" }}
        >
          <div style={{ color: iconBg }}>{icon}</div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {subtitle && (
          <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
        )}
        {trend && (
          trendHref ? (
            <Link
              href={trendHref}
              className={`text-xs mt-1 font-medium underline underline-offset-2 ${
                trendUp ? "text-emerald-600" : "text-red-500"
              }`}
            >
              {trend}
            </Link>
          ) : (
            <p
              className={`text-xs mt-1 font-medium ${
                trendUp ? "text-emerald-600" : "text-red-500"
              }`}
            >
              {trend}
            </p>
          )
        )}
      </CardContent>
    </Card>
  )
}

const PERIODS = [
  { label: "1 Week",   days: 7 },
  { label: "15 Days",  days: 15 },
  { label: "1 Month",  days: 30 },
  { label: "1 Quarter",days: 90 },
]

export default function DashboardPage() {
  const [kpis, setKpis] = useState<KPIs | null>(null)
  const [trend, setTrend] = useState<TrendRow[]>([])
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(true)
  const [trendDays, setTrendDays] = useState(14)
  const [customDays, setCustomDays] = useState("")
  const [trendLoading, setTrendLoading] = useState(false)
  const currency = useCurrency()

  useEffect(() => {
    Promise.all([fetchKPIs(), fetchTrend(trendDays)])
      .then(([k, t]) => { setKpis(k); setTrend(t) })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  function handlePeriodChange(days: number) {
    setTrendDays(days)
    setCustomDays("")
    setTrendLoading(true)
    fetchTrend(days)
      .then(setTrend)
      .catch(() => {})
      .finally(() => setTrendLoading(false))
  }

  function handleMonthSelect(value: string) {
    if (!value) return
    setCustomDays(value)
    const [year, month] = value.split("-").map(Number)
    const start = new Date(year, month - 1, 1)
    const today = new Date()
    const days = Math.max(1, Math.ceil((today.getTime() - start.getTime()) / 86400000))
    setTrendDays(days)
    setTrendLoading(true)
    fetchTrend(days)
      .then(setTrend)
      .catch(() => {})
      .finally(() => setTrendLoading(false))
  }

  // Build last 12 months for the dropdown
  const monthOptions = Array.from({ length: 12 }, (_, i) => {
    const d = new Date()
    d.setDate(1)
    d.setMonth(d.getMonth() - i)
    const value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`
    const label = d.toLocaleString("default", { month: "long", year: "numeric" })
    return { value, label }
  })

  const recentActivity = trend.slice(0, 5).map((row) => ({
    date: row.date,
    total: row.total,
  }))

  return (
    <AppLayout activePage="dashboard">
      <div className="px-6 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            Real-time overview of your business
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-destructive/10 border border-destructive/20 text-destructive rounded-lg text-sm">
            Could not load data: {error}. Make sure the BzHub API is running.
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center space-y-2">
              <div
                className="h-8 w-8 rounded-full border-4 border-t-transparent animate-spin mx-auto"
                style={{ borderColor: "#6D28D9", borderTopColor: "transparent" }}
              />
              <p className="text-muted-foreground text-sm">Loading dashboard…</p>
            </div>
          </div>
        ) : kpis ? (
          <>
            {/* KPI Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4 mb-8">
              <KPICard
                title="Today's Sales"
                value={`${currency}${kpis.today_sales.toLocaleString("en-US", { minimumFractionDigits: 2 })}`}
                icon={<DollarSign className="h-4 w-4" />}
                iconBg="#6D28D9"
                trend="Revenue today"
              />
              <KPICard
                title="Inventory Value"
                value={`${currency}${kpis.inventory_value.toLocaleString("en-US", { minimumFractionDigits: 2 })}`}
                subtitle={`${kpis.total_items} items`}
                icon={<Package className="h-4 w-4" />}
                iconBg="#0EA5E9"
              />
              <KPICard
                title="Low Stock"
                value={String(kpis.low_stock_count)}
                subtitle="items below threshold"
                trend={kpis.low_stock_count > 0 ? "Needs attention" : "All stocked"}
                trendUp={kpis.low_stock_count === 0}
                trendHref={kpis.low_stock_count > 0 ? "/operations?filter=lowstock" : undefined}
                icon={<AlertTriangle className="h-4 w-4" />}
                iconBg={kpis.low_stock_count > 0 ? "#EF4444" : "#10B981"}
              />
              <KPICard
                title="Pipeline Value"
                value={`${currency}${kpis.pipeline_value.toLocaleString("en-US", { minimumFractionDigits: 2 })}`}
                subtitle={`${kpis.conversion_rate}% conversion`}
                icon={<Users className="h-4 w-4" />}
                iconBg="#8B5CF6"
              />
              <KPICard
                title="Avg Daily Sales"
                value={`${currency}${kpis.avg_daily_sales.toLocaleString("en-US", { minimumFractionDigits: 2 })}`}
                subtitle="14-day average"
                icon={<BarChart3 className="h-4 w-4" />}
                iconBg="#F59E0B"
              />
              <KPICard
                title="Growth (7d)"
                value={`${kpis.growth_pct >= 0 ? "+" : ""}${kpis.growth_pct}%`}
                trend={kpis.growth_pct >= 0 ? "Up from last week" : "Down from last week"}
                trendUp={kpis.growth_pct >= 0}
                icon={<TrendingUp className="h-4 w-4" />}
                iconBg={kpis.growth_pct >= 0 ? "#10B981" : "#EF4444"}
              />
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
              {/* Sales Trend */}
              <Card className="xl:col-span-2">
                <CardHeader className="pb-3">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                    <CardTitle className="text-base">
                      Sales Trend — Last {trendDays} Days
                    </CardTitle>
                    <div className="flex flex-wrap items-center gap-1.5">
                      {PERIODS.map((p) => (
                        <button
                          key={p.days}
                          onClick={() => handlePeriodChange(p.days)}
                          className={`px-2.5 py-1 rounded-md text-xs font-medium transition-colors border ${
                            trendDays === p.days && !customDays
                              ? "text-white border-transparent"
                              : "text-muted-foreground border-border hover:bg-muted"
                          }`}
                          style={trendDays === p.days && !customDays ? { backgroundColor: "#6D28D9", borderColor: "#6D28D9" } : {}}
                        >
                          {p.label}
                        </button>
                      ))}
                      <select
                        value={customDays}
                        onChange={(e) => handleMonthSelect(e.target.value)}
                        className="h-7 px-2 text-xs rounded-md border border-border bg-background focus:outline-none"
                      >
                        <option value="">Month…</option>
                        {monthOptions.map((m) => (
                          <option key={m.value} value={m.value}>{m.label}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {trendLoading ? (
                    <div className="animate-pulse h-[280px] bg-muted rounded-lg" />
                  ) : trend.length === 0 ? (
                    <p className="text-muted-foreground text-sm italic">
                      No sales data available.
                    </p>
                  ) : (
                    <ResponsiveContainer width="100%" height={280}>
                      <LineChart data={trend}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                        <YAxis tick={{ fontSize: 11 }} />
                        <Tooltip />
                        <Line
                          type="monotone"
                          dataKey="total"
                          stroke="#6D28D9"
                          strokeWidth={2}
                          dot={false}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  )}
                </CardContent>
              </Card>

              {/* Recent Activity */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Recent Activity</CardTitle>
                </CardHeader>
                <CardContent>
                  {recentActivity.length === 0 ? (
                    <p className="text-muted-foreground text-sm italic">
                      No recent activity.
                    </p>
                  ) : (
                    <div className="space-y-3">
                      {recentActivity.map((row) => (
                        <div
                          key={row.date}
                          className="flex items-center justify-between py-2 border-b border-border last:border-0"
                        >
                          <div className="flex items-center gap-2">
                            <div
                              className="h-2 w-2 rounded-full flex-shrink-0"
                              style={{ backgroundColor: "#6D28D9" }}
                            />
                            <span className="text-sm text-muted-foreground">
                              {row.date}
                            </span>
                          </div>
                          <Badge variant={row.total > 0 ? "default" : "secondary"}>
                            {currency}{row.total.toFixed(2)}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </>
        ) : null}
      </div>
    </AppLayout>
  )
}
