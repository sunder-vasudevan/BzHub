"use client"

import { useEffect, useState } from "react"
import AppLayout from "@/components/layout/AppLayout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
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
  icon: React.ReactNode
  iconBg: string
}

function KPICard({ title, value, subtitle, trend, trendUp, icon, iconBg }: KPICardProps) {
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
          <p
            className={`text-xs mt-1 font-medium ${
              trendUp ? "text-emerald-600" : "text-red-500"
            }`}
          >
            {trend}
          </p>
        )}
      </CardContent>
    </Card>
  )
}

// NOTE: Future chart integration point — replace the trend table below with a
// Recharts <LineChart> or <BarChart> component once recharts is installed.
// Example: import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"

export default function DashboardPage() {
  const [kpis, setKpis] = useState<KPIs | null>(null)
  const [trend, setTrend] = useState<TrendRow[]>([])
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([fetchKPIs(), fetchTrend(14)])
      .then(([k, t]) => {
        setKpis(k)
        setTrend(t)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

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
            Could not load data: {error}. Make sure the BizHub API is running.
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
                value={`$${kpis.today_sales.toLocaleString("en-US", { minimumFractionDigits: 2 })}`}
                icon={<DollarSign className="h-4 w-4" />}
                iconBg="#6D28D9"
                trend="Revenue today"
              />
              <KPICard
                title="Inventory Value"
                value={`$${kpis.inventory_value.toLocaleString("en-US", { minimumFractionDigits: 2 })}`}
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
                icon={<AlertTriangle className="h-4 w-4" />}
                iconBg={kpis.low_stock_count > 0 ? "#EF4444" : "#10B981"}
              />
              <KPICard
                title="Pipeline Value"
                value={`$${kpis.pipeline_value.toLocaleString("en-US", { minimumFractionDigits: 2 })}`}
                subtitle={`${kpis.conversion_rate}% conversion`}
                icon={<Users className="h-4 w-4" />}
                iconBg="#8B5CF6"
              />
              <KPICard
                title="Avg Daily Sales"
                value={`$${kpis.avg_daily_sales.toLocaleString("en-US", { minimumFractionDigits: 2 })}`}
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
                <CardHeader>
                  <CardTitle className="text-base">
                    Sales Trend — Last 14 Days
                  </CardTitle>
                  {/* TODO: Replace table with <BarChart> from recharts once installed */}
                </CardHeader>
                <CardContent>
                  {trend.length === 0 ? (
                    <p className="text-muted-foreground text-sm italic">
                      No sales data available.
                    </p>
                  ) : (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Date</TableHead>
                          <TableHead className="text-right">Total Sales</TableHead>
                          <TableHead>Bar</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {trend.map((row) => {
                          const maxTotal = Math.max(...trend.map((r) => r.total), 1)
                          const pct = Math.round((row.total / maxTotal) * 100)
                          return (
                            <TableRow key={row.date}>
                              <TableCell className="text-muted-foreground">
                                {row.date}
                              </TableCell>
                              <TableCell className="text-right font-medium">
                                ${row.total.toFixed(2)}
                              </TableCell>
                              <TableCell>
                                <div className="h-2 rounded-full bg-muted w-32">
                                  <div
                                    className="h-2 rounded-full"
                                    style={{
                                      width: `${pct}%`,
                                      backgroundColor: "#6D28D9",
                                    }}
                                  />
                                </div>
                              </TableCell>
                            </TableRow>
                          )
                        })}
                      </TableBody>
                    </Table>
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
                            ${row.total.toFixed(2)}
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
