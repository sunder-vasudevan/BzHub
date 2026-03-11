"use client"

import { useEffect, useState, useCallback } from "react"
import AppLayout from "@/components/layout/AppLayout"
import { Card, CardContent } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { fetchSales, fetchInventory } from "@/lib/db"
import { useCurrency } from "@/hooks/useCurrency"
import { BarChart3, TrendingUp, Package } from "lucide-react"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"

type Tab = "sales" | "topsellers" | "inventory"

// ---- Types ----
interface SaleRow {
  id: number
  sale_date: string
  item_name: string
  quantity: number
  total_amount: number
}

interface InventoryRow {
  id: string
  item_name: string
  description?: string
  quantity: number
  cost_price: number
  sale_price: number
  threshold?: number
}

interface MonthlySummary {
  month: string
  revenue: number
  numSales: number
  avgOrder: number
}

interface TopSeller {
  item_name: string
  qty_sold: number
}

// ---- Sales Report Tab ----
function SalesReportTab() {
  const [summary, setSummary] = useState<MonthlySummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const currency = useCurrency()

  const load = useCallback(async () => {
    try {
      setError("")
      const sales: SaleRow[] = await fetchSales()
      // Aggregate by month (YYYY-MM)
      const map: Record<string, { revenue: number; count: number }> = {}
      for (const s of sales) {
        const month = (s.sale_date ?? "").slice(0, 7)
        if (!month) continue
        if (!map[month]) map[month] = { revenue: 0, count: 0 }
        map[month].revenue += s.total_amount ?? 0
        map[month].count += 1
      }
      const result: MonthlySummary[] = Object.entries(map)
        .map(([month, v]) => ({
          month,
          revenue: Math.round(v.revenue * 100) / 100,
          numSales: v.count,
          avgOrder: v.count > 0 ? Math.round((v.revenue / v.count) * 100) / 100 : 0,
        }))
        .sort((a, b) => b.month.localeCompare(a.month))
      setSummary(result)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load sales")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const totalRevenue = summary.reduce((s, r) => s + r.revenue, 0)
  const totalSales = summary.reduce((s, r) => s + r.numSales, 0)

  return (
    <div className="space-y-4">
      {error && (
        <div className="p-3 bg-destructive/10 border border-destructive/20 text-destructive rounded-lg text-sm">
          {error}
        </div>
      )}

      {!loading && summary.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="bg-violet-50 border border-violet-100 rounded-xl p-4">
            <p className="text-xs text-muted-foreground">Total Revenue</p>
            <p className="text-xl font-bold" style={{ color: "#6D28D9" }}>
              {currency}{totalRevenue.toLocaleString("en-US", { minimumFractionDigits: 2 })}
            </p>
          </div>
          <div className="bg-violet-50 border border-violet-100 rounded-xl p-4">
            <p className="text-xs text-muted-foreground">Total Transactions</p>
            <p className="text-xl font-bold" style={{ color: "#6D28D9" }}>{totalSales}</p>
          </div>
          <div className="bg-violet-50 border border-violet-100 rounded-xl p-4">
            <p className="text-xs text-muted-foreground">Months on Record</p>
            <p className="text-xl font-bold" style={{ color: "#6D28D9" }}>{summary.length}</p>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div
            className="h-8 w-8 rounded-full border-4 border-t-transparent animate-spin"
            style={{ borderColor: "#6D28D9", borderTopColor: "transparent" }}
          />
        </div>
      ) : (
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Month</TableHead>
                <TableHead className="text-right">Total Revenue</TableHead>
                <TableHead className="text-right">No. of Sales</TableHead>
                <TableHead className="text-right">Avg Order Value</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {summary.map((row) => (
                <TableRow key={row.month}>
                  <TableCell className="font-medium">{row.month}</TableCell>
                  <TableCell className="text-right font-semibold" style={{ color: "#6D28D9" }}>
                    {currency}{row.revenue.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                  </TableCell>
                  <TableCell className="text-right">{row.numSales}</TableCell>
                  <TableCell className="text-right text-muted-foreground">
                    {currency}{row.avgOrder.toFixed(2)}
                  </TableCell>
                </TableRow>
              ))}
              {summary.length === 0 && (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-muted-foreground italic py-8">
                    No sales data found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  )
}

// ---- Top Sellers Tab ----
function TopSellersTab() {
  const [data, setData] = useState<TopSeller[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  const load = useCallback(async () => {
    try {
      setError("")
      const sales: SaleRow[] = await fetchSales()
      const map: Record<string, number> = {}
      for (const s of sales) {
        const name = s.item_name ?? "Unknown"
        map[name] = (map[name] ?? 0) + (s.quantity ?? 0)
      }
      const sorted: TopSeller[] = Object.entries(map)
        .map(([item_name, qty_sold]) => ({ item_name, qty_sold }))
        .sort((a, b) => b.qty_sold - a.qty_sold)
        .slice(0, 10)
      setData(sorted)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load data")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  return (
    <div className="space-y-4">
      {error && (
        <div className="p-3 bg-destructive/10 border border-destructive/20 text-destructive rounded-lg text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div
            className="h-8 w-8 rounded-full border-4 border-t-transparent animate-spin"
            style={{ borderColor: "#6D28D9", borderTopColor: "transparent" }}
          />
        </div>
      ) : data.length === 0 ? (
        <p className="text-muted-foreground text-sm italic py-8 text-center">No sales data available.</p>
      ) : (
        <>
          <p className="text-sm text-muted-foreground">Top 10 products by total quantity sold (all time)</p>
          <ResponsiveContainer width="100%" height={360}>
            <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 80 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="item_name"
                tick={{ fontSize: 11 }}
                angle={-35}
                textAnchor="end"
                interval={0}
              />
              <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
              <Tooltip
                formatter={(value: number) => [`${value} units`, "Qty Sold"]}
              />
              <Bar dataKey="qty_sold" fill="#6D28D9" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>

          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-10">#</TableHead>
                  <TableHead>Product</TableHead>
                  <TableHead className="text-right">Units Sold</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.map((row, i) => (
                  <TableRow key={row.item_name}>
                    <TableCell className="text-muted-foreground text-sm">{i + 1}</TableCell>
                    <TableCell className="font-medium">{row.item_name}</TableCell>
                    <TableCell className="text-right font-semibold" style={{ color: "#6D28D9" }}>
                      {row.qty_sold}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </>
      )}
    </div>
  )
}

// ---- Inventory Report Tab ----
function InventoryReportTab() {
  const [items, setItems] = useState<InventoryRow[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const currency = useCurrency()

  const load = useCallback(async () => {
    try {
      setError("")
      const data: InventoryRow[] = await fetchInventory()
      setItems(data)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load inventory")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const totalValue = items.reduce(
    (s, i) => s + (i.quantity ?? 0) * (i.sale_price ?? 0),
    0
  )
  const lowStockCount = items.filter((i) => (i.quantity ?? 0) < 10).length

  return (
    <div className="space-y-4">
      {error && (
        <div className="p-3 bg-destructive/10 border border-destructive/20 text-destructive rounded-lg text-sm">
          {error}
        </div>
      )}

      {!loading && items.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div className="bg-violet-50 border border-violet-100 rounded-xl p-4">
            <p className="text-xs text-muted-foreground">Total Items</p>
            <p className="text-xl font-bold" style={{ color: "#6D28D9" }}>{items.length}</p>
          </div>
          <div className="bg-violet-50 border border-violet-100 rounded-xl p-4">
            <p className="text-xs text-muted-foreground">Total Inventory Value</p>
            <p className="text-xl font-bold" style={{ color: "#6D28D9" }}>
              {currency}{totalValue.toLocaleString("en-US", { minimumFractionDigits: 2 })}
            </p>
          </div>
          <div className="bg-red-50 border border-red-100 rounded-xl p-4">
            <p className="text-xs text-muted-foreground">Low Stock Items</p>
            <p className="text-xl font-bold text-red-600">{lowStockCount}</p>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div
            className="h-8 w-8 rounded-full border-4 border-t-transparent animate-spin"
            style={{ borderColor: "#6D28D9", borderTopColor: "transparent" }}
          />
        </div>
      ) : (
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Category</TableHead>
                <TableHead className="text-right">Stock Qty</TableHead>
                <TableHead className="text-right">Unit Price</TableHead>
                <TableHead className="text-right">Total Value</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((item) => {
                const totalVal = (item.quantity ?? 0) * (item.sale_price ?? 0)
                const isLowStock = (item.quantity ?? 0) < 10
                return (
                  <TableRow key={item.id}>
                    <TableCell className="font-medium">{item.item_name}</TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {item.description || "—"}
                    </TableCell>
                    <TableCell className="text-right">{item.quantity}</TableCell>
                    <TableCell className="text-right text-muted-foreground">
                      {currency}{Number(item.sale_price ?? 0).toFixed(2)}
                    </TableCell>
                    <TableCell className="text-right font-semibold">
                      {currency}{totalVal.toFixed(2)}
                    </TableCell>
                    <TableCell>
                      {isLowStock ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-700">
                          Low Stock
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700">
                          OK
                        </span>
                      )}
                    </TableCell>
                  </TableRow>
                )
              })}
              {items.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-muted-foreground italic py-8">
                    No inventory data found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  )
}

// ---- Main Page ----
export default function ReportsPage() {
  const [activeTab, setActiveTab] = useState<Tab>("sales")

  const tabs: { key: Tab; label: string; icon: React.ReactNode }[] = [
    { key: "sales", label: "Sales Report", icon: <TrendingUp className="h-4 w-4" /> },
    { key: "topsellers", label: "Top Sellers", icon: <BarChart3 className="h-4 w-4" /> },
    { key: "inventory", label: "Inventory Report", icon: <Package className="h-4 w-4" /> },
  ]

  return (
    <AppLayout activePage="reports">
      <div className="px-4 py-4 md:px-6 md:py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold">Reports</h1>
          <p className="text-sm text-muted-foreground">Sales analytics, top sellers, and inventory overview</p>
        </div>

        <div className="flex gap-1 mb-6 bg-white rounded-xl p-1 shadow-sm w-fit border border-border flex-wrap">
          {tabs.map((t) => (
            <button
              key={t.key}
              onClick={() => setActiveTab(t.key)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                activeTab === t.key
                  ? "text-white"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted"
              }`}
              style={activeTab === t.key ? { backgroundColor: "#6D28D9" } : undefined}
            >
              {t.icon}
              {t.label}
            </button>
          ))}
        </div>

        <Card>
          <CardContent className="p-6">
            {activeTab === "sales" && <SalesReportTab />}
            {activeTab === "topsellers" && <TopSellersTab />}
            {activeTab === "inventory" && <InventoryReportTab />}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
