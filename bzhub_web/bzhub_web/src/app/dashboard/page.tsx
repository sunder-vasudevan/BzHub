"use client"

import { useEffect, useRef, useState } from "react"
import Link from "next/link"
import AppLayout from "@/components/layout/AppLayout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { fetchKPIs, fetchTrend, fetchProductVelocity, fetchInsights, Insight } from "@/lib/db"
import {
  DollarSign,
  Package,
  AlertTriangle,
  Users,
  TrendingUp,
  BarChart3,
  Settings2,
  Lightbulb,
  ChevronDown,
  ChevronUp,
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

interface VelocityItem {
  item_name: string
  qty_sold: number
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
  { label: "7 Days",   days: 7 },
  { label: "30 Days",  days: 30 },
  { label: "90 Days",  days: 90 },
]

const KPI_KEYS = [
  "today_sales",
  "inventory_value",
  "low_stock",
  "avg_daily_sales",
  "pipeline_value",
  "growth",
] as const
type KPIKey = typeof KPI_KEYS[number]

const KPI_LABELS: Record<KPIKey, string> = {
  today_sales: "Today's Sales",
  inventory_value: "Inventory Value",
  low_stock: "Low Stock",
  avg_daily_sales: "Avg Daily Sales",
  pipeline_value: "Pipeline Value",
  growth: "Growth (7d)",
}

const PREFS_KEY = "bzhub_dashboard_prefs"

interface DashboardPrefs {
  visibleKPIs: Record<KPIKey, boolean>
  trendDays: number
}

function loadPrefs(): DashboardPrefs {
  try {
    const raw = localStorage.getItem(PREFS_KEY)
    if (raw) return JSON.parse(raw) as DashboardPrefs
  } catch {}
  return {
    visibleKPIs: {
      today_sales: true,
      inventory_value: true,
      low_stock: true,
      avg_daily_sales: true,
      pipeline_value: true,
      growth: true,
    },
    trendDays: 30,
  }
}

function savePrefs(prefs: DashboardPrefs) {
  try {
    localStorage.setItem(PREFS_KEY, JSON.stringify(prefs))
  } catch {}
}

function compactINR(n: number): string {
  if (n >= 1e7) return `${(n / 1e7).toFixed(2)} Cr`
  if (n >= 1e5) return `${(n / 1e5).toFixed(2)} L`
  if (n >= 1e3) return `${(n / 1e3).toFixed(1)} K`
  return n.toFixed(2)
}

export default function DashboardPage() {
  const [kpis, setKpis] = useState<KPIs | null>(null)
  const [trend, setTrend] = useState<TrendRow[]>([])
  const [velocity, setVelocity] = useState<{ fast: VelocityItem[]; slow: VelocityItem[] }>({ fast: [], slow: [] })
  const [insights, setInsights] = useState<Insight[]>([])
  const [insightsOpen, setInsightsOpen] = useState(true)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(true)
  const [trendDays, setTrendDays] = useState(30)
  const [customDays, setCustomDays] = useState("")
  const [trendLoading, setTrendLoading] = useState(false)
  const currency = useCurrency()

  // Dashboard customization
  const [prefs, setPrefs] = useState<DashboardPrefs>(() => loadPrefs())
  const [customizeOpen, setCustomizeOpen] = useState(false)
  const customizeRef = useRef<HTMLDivElement>(null)

  // Sync trendDays from prefs on mount
  useEffect(() => {
    const saved = loadPrefs()
    setPrefs(saved)
    setTrendDays(saved.trendDays)
  }, [])

  // Close customize dropdown on outside click
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (customizeRef.current && !customizeRef.current.contains(e.target as Node)) {
        setCustomizeOpen(false)
      }
    }
    if (customizeOpen) document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [customizeOpen])

  function toggleKPI(key: KPIKey) {
    const updated = {
      ...prefs,
      visibleKPIs: { ...prefs.visibleKPIs, [key]: !prefs.visibleKPIs[key] },
    }
    setPrefs(updated)
    savePrefs(updated)
  }

  useEffect(() => {
    Promise.all([
      fetchKPIs(),
      fetchTrend(trendDays),
      fetchProductVelocity(30).catch(() => ({ fast: [], slow: [] })),
    ])
      .then(([k, t, v]) => { setKpis(k); setTrend(t); setVelocity(v) })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
    fetchInsights().then(setInsights).catch(() => {})
  }, [])

  function handlePeriodChange(days: number) {
    setTrendDays(days)
    setCustomDays("")
    setTrendLoading(true)
    fetchTrend(days)
      .then(setTrend)
      .catch(() => {})
      .finally(() => setTrendLoading(false))
    const updated = { ...prefs, trendDays: days }
    setPrefs(updated)
    savePrefs(updated)
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
      <div className="px-4 py-4 md:px-6 md:py-8">
        <div className="mb-6 flex items-start justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
            <p className="text-sm text-muted-foreground">
              Real-time overview of your business
            </p>
          </div>
          {/* Customize button */}
          <div className="relative" ref={customizeRef}>
            <Button variant="outline" size="sm" onClick={() => setCustomizeOpen(!customizeOpen)}>
              <Settings2 className="h-4 w-4 mr-2" />
              Customize
            </Button>
            {customizeOpen && (
              <div className="absolute right-0 top-full mt-2 w-56 bg-white border border-border rounded-xl shadow-xl z-30 overflow-hidden">
                <div className="px-3 py-2 border-b border-border">
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Show / Hide Cards</p>
                </div>
                <ul className="py-1">
                  {KPI_KEYS.map(key => (
                    <li key={key}>
                      <label className="flex items-center gap-2.5 px-3 py-2 hover:bg-muted cursor-pointer text-sm">
                        <input
                          type="checkbox"
                          checked={prefs.visibleKPIs[key]}
                          onChange={() => toggleKPI(key)}
                          className="rounded"
                        />
                        {KPI_LABELS[key]}
                      </label>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
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
                style={{ borderColor: "var(--brand-color)", borderTopColor: "transparent" }}
              />
              <p className="text-muted-foreground text-sm">Loading dashboard…</p>
            </div>
          </div>
        ) : kpis ? (
          <>
            {/* KPI Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4 mb-8">
              {prefs.visibleKPIs.today_sales && (
                <KPICard
                  title="Today's Sales"
                  value={`${currency}${kpis.today_sales.toLocaleString("en-US", { minimumFractionDigits: 2 })}`}
                  icon={<DollarSign className="h-4 w-4" />}
                  iconBg="var(--brand-color)"
                  trend="Revenue today"
                />
              )}
              {prefs.visibleKPIs.inventory_value && (
                <KPICard
                  title="Inventory Value"
                  value={`${currency}${compactINR(kpis.inventory_value)}`}
                  subtitle={`${kpis.total_items} items`}
                  icon={<Package className="h-4 w-4" />}
                  iconBg="#0EA5E9"
                />
              )}
              {prefs.visibleKPIs.low_stock && (
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
              )}
              {prefs.visibleKPIs.pipeline_value && (
                <KPICard
                  title="Pipeline Value"
                  value={`${currency}${kpis.pipeline_value.toLocaleString("en-US", { minimumFractionDigits: 2 })}`}
                  subtitle={`${kpis.conversion_rate}% conversion`}
                  icon={<Users className="h-4 w-4" />}
                  iconBg="#8B5CF6"
                />
              )}
              {prefs.visibleKPIs.avg_daily_sales && (
                <KPICard
                  title="Avg Daily Sales"
                  value={`${currency}${kpis.avg_daily_sales.toLocaleString("en-US", { minimumFractionDigits: 2 })}`}
                  subtitle="30-day average"
                  icon={<BarChart3 className="h-4 w-4" />}
                  iconBg="#F59E0B"
                />
              )}
              {prefs.visibleKPIs.growth && (
                <KPICard
                  title="Growth (7d)"
                  value={`${kpis.growth_pct >= 0 ? "+" : ""}${kpis.growth_pct}%`}
                  trend={kpis.growth_pct >= 0 ? "Up from last week" : "Down from last week"}
                  trendUp={kpis.growth_pct >= 0}
                  icon={<TrendingUp className="h-4 w-4" />}
                  iconBg={kpis.growth_pct >= 0 ? "#10B981" : "#EF4444"}
                />
              )}
            </div>

            {/* AI Insights */}
            {insights.length > 0 && (() => {
              const GROUP_CONFIG: Record<string, { label: string; icon: string; color: string }> = {
                Inventory:  { label: 'Inventory',  icon: '📦', color: '#0EA5E9' },
                HR:         { label: 'HR',          icon: '👥', color: '#8B5CF6' },
                Operations: { label: 'Operations',  icon: '⚙️', color: '#F59E0B' },
                Sales:      { label: 'Sales',       icon: '📈', color: '#10B981' },
              }
              const groups = ['Inventory', 'HR', 'Operations', 'Sales'] as const
              const warningCount = insights.filter(i => i.severity === 'warning').length
              return (
                <Card className="mb-6">
                  <CardHeader className="pb-2 cursor-pointer select-none" onClick={() => setInsightsOpen(o => !o)}>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm flex items-center gap-2">
                        <Lightbulb className="h-4 w-4" style={{ color: "var(--brand-color)" }} />
                        Smart Insights
                        {warningCount > 0 && (
                          <span className="text-xs font-medium text-amber-600">
                            · {warningCount} action{warningCount > 1 ? 's' : ''} needed
                          </span>
                        )}
                      </CardTitle>
                      {insightsOpen ? <ChevronUp className="h-4 w-4 text-muted-foreground" /> : <ChevronDown className="h-4 w-4 text-muted-foreground" />}
                    </div>
                  </CardHeader>
                  {insightsOpen && (
                    <CardContent className="pt-0">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {groups.map((group) => {
                          const groupInsights = insights.filter(i => i.group === group)
                          if (groupInsights.length === 0) return null
                          const cfg = GROUP_CONFIG[group]
                          return (
                            <div key={group} className="rounded-lg border border-border p-3">
                              <div className="flex items-center gap-2 mb-2">
                                <span className="text-base leading-none">{cfg.icon}</span>
                                <span className="text-xs font-semibold uppercase tracking-wide" style={{ color: cfg.color }}>{cfg.label}</span>
                              </div>
                              <ul className="space-y-1.5">
                                {groupInsights.map((insight) => (
                                  <li key={insight.id} className="flex items-start gap-2">
                                    <span
                                      className="h-1.5 w-1.5 rounded-full flex-shrink-0 mt-1.5"
                                      style={{ backgroundColor: insight.severity === 'warning' ? '#F59E0B' : '#94A3B8' }}
                                    />
                                    <span className="text-xs text-foreground flex-1 leading-relaxed">
                                      {insight.message}
                                      {insight.href && (
                                        <Link href={insight.href} className="ml-1.5 underline underline-offset-2 font-medium" style={{ color: cfg.color }}>
                                          View →
                                        </Link>
                                      )}
                                    </span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )
                        })}
                      </div>
                    </CardContent>
                  )}
                </Card>
              )
            })()}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              {/* Fast Movers */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-emerald-600" />
                    Fast-Moving Products <span className="text-muted-foreground font-normal text-xs">(last 30 days)</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {velocity.fast.length === 0 ? (
                    <p className="text-muted-foreground text-xs italic">No sales data yet.</p>
                  ) : (
                    <div className="space-y-2">
                      {velocity.fast.map((item, i) => (
                        <div key={item.item_name} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-emerald-600 w-4">{i + 1}</span>
                            <span className="text-sm truncate max-w-[160px]">{item.item_name}</span>
                          </div>
                          <div className="text-right flex-shrink-0">
                            <span className="text-xs font-semibold">{item.qty_sold} units</span>
                            <span className="text-xs text-muted-foreground ml-2">{currency}{item.total.toFixed(0)}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Slow Movers */}
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm flex items-center gap-2">
                    <BarChart3 className="h-4 w-4 text-amber-500" />
                    Slow-Moving Products <span className="text-muted-foreground font-normal text-xs">(last 30 days)</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {velocity.slow.length === 0 ? (
                    <p className="text-muted-foreground text-xs italic">No sales data yet.</p>
                  ) : (
                    <div className="space-y-2">
                      {velocity.slow.map((item, i) => (
                        <div key={item.item_name} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-amber-500 w-4">{i + 1}</span>
                            <span className="text-sm truncate max-w-[160px]">{item.item_name}</span>
                          </div>
                          <div className="text-right flex-shrink-0">
                            <span className="text-xs font-semibold">{item.qty_sold} units</span>
                            <span className="text-xs text-muted-foreground ml-2">{currency}{item.total.toFixed(0)}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
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
                          style={trendDays === p.days && !customDays ? { backgroundColor: "var(--brand-color)", borderColor: "var(--brand-color)" } : {}}
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
                          stroke="var(--brand-color)"
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
                              style={{ backgroundColor: "var(--brand-color)" }}
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
