"use client"

import { useEffect, useState, useCallback, useRef, Suspense } from "react"
import { useSearchParams } from "next/navigation"
import AppLayout from "@/components/layout/AppLayout"
import { toast } from "@/components/ui/toast"
import { useCurrency } from "@/hooks/useCurrency"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog"
import {
  fetchInventory,
  createInventoryItem,
  updateInventoryItem,
  deleteInventoryItem,
  fetchSales,
} from "@/lib/api"
import {
  Plus,
  Search,
  ShoppingCart,
  Package,
  Receipt,
  AlertTriangle,
  ChevronUp,
  ChevronDown,
  ChevronsUpDown,
} from "lucide-react"

type Tab = "inventory" | "pos" | "bills"
type SortDir = "asc" | "desc" | "none"

interface InventoryItem {
  id: string
  item_name: string
  quantity: number
  threshold: number
  cost_price: number
  sale_price: number
  description: string
  image_path?: string
}

interface Sale {
  id: number
  sale_date: string
  item_name: string
  quantity: number
  sale_price: number
  total_amount: number
  username: string
}

type InvSortKey = "item_name" | "quantity" | "cost_price" | "sale_price" | "status"
type BillSortKey = "sale_date" | "item_name" | "quantity" | "total_amount"

// ---- SortIcon ----
function SortIcon({ active, dir }: { active: boolean; dir: SortDir }) {
  if (!active || dir === "none") return <ChevronsUpDown className="h-3 w-3 ml-1 inline opacity-40" />
  if (dir === "asc") return <ChevronUp className="h-3 w-3 ml-1 inline" />
  return <ChevronDown className="h-3 w-3 ml-1 inline" />
}

function useSortState<K extends string>(defaultKey: K) {
  const [sortKey, setSortKey] = useState<K>(defaultKey)
  const [sortDir, setSortDir] = useState<SortDir>("none")

  function toggleSort(key: K) {
    if (sortKey !== key) {
      setSortKey(key)
      setSortDir("asc")
    } else {
      setSortDir((d) => (d === "none" ? "asc" : d === "asc" ? "desc" : "none"))
    }
  }

  function SH({ k, children, className }: { k: K; children: React.ReactNode; className?: string }) {
    return (
      <TableHead
        className={`cursor-pointer select-none whitespace-nowrap ${className ?? ""}`}
        onClick={() => toggleSort(k)}
      >
        {children}
        <SortIcon active={sortKey === k} dir={sortKey === k ? sortDir : "none"} />
      </TableHead>
    )
  }

  return { sortKey, sortDir, SH }
}

// ---- stockStatus ----
function stockStatus(item: InventoryItem): { label: string; bg: string; color: string } {
  if (item.quantity === 0)
    return { label: "Out of Stock", bg: "#7F1D1D", color: "#fff" }
  const ratio = item.threshold > 0 ? item.quantity / item.threshold : 2
  if (ratio <= 0.25)
    return { label: "Critical", bg: "#DC2626", color: "#fff" }
  if (ratio <= 0.5)
    return { label: "Very Low", bg: "#F87171", color: "#7F1D1D" }
  if (ratio <= 1.0)
    return { label: "Low Stock", bg: "#FEE2E2", color: "#B91C1C" }
  return { label: "In Stock", bg: "#D1FAE5", color: "#065F46" }
}

function statusOrder(item: InventoryItem): number {
  const s = stockStatus(item).label
  return ["Out of Stock", "Critical", "Very Low", "Low Stock", "In Stock"].indexOf(s)
}

// ---- Inventory Tab ----
function InventoryTab({ lowStockOnly = false }: { lowStockOnly?: boolean }) {
  const [items, setItems] = useState<InventoryItem[]>([])
  const [filtered, setFiltered] = useState<InventoryItem[]>([])
  const [search, setSearch] = useState("")
  const [showLowStock, setShowLowStock] = useState(lowStockOnly)
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [editing, setEditing] = useState<InventoryItem | null>(null)
  const currency = useCurrency()
  const { sortKey, sortDir, SH } = useSortState<InvSortKey>("item_name")

  const load = useCallback(async () => {
    const d = await fetchInventory().catch(() => [])
    setItems(d)
    setLoading(false)
  }, [])

  useEffect(() => { load() }, [load])

  useEffect(() => {
    const q = search.toLowerCase()
    let base = items
    if (showLowStock) base = items.filter((i) => i.quantity <= i.threshold)
    let result = q
      ? base.filter(
          (i) =>
            (i.item_name || "").toLowerCase().includes(q) ||
            (i.description || "").toLowerCase().includes(q)
        )
      : base

    if (sortDir !== "none") {
      result = [...result].sort((a, b) => {
        let cmp = 0
        if (sortKey === "item_name") cmp = (a.item_name || "").localeCompare(b.item_name || "")
        else if (sortKey === "quantity") cmp = a.quantity - b.quantity
        else if (sortKey === "cost_price") cmp = a.cost_price - b.cost_price
        else if (sortKey === "sale_price") cmp = a.sale_price - b.sale_price
        else if (sortKey === "status") cmp = statusOrder(a) - statusOrder(b)
        return sortDir === "asc" ? cmp : -cmp
      })
    }

    setFiltered(result)
  }, [search, items, showLowStock, sortKey, sortDir])

  async function handleDelete(name: string) {
    if (!confirm(`Delete "${name}"?`)) return
    try {
      await deleteInventoryItem(name)
      await load()
      toast("Item deleted", "success")
    } catch {
      toast("Failed to delete item", "error")
    }
  }

  async function handleSave(
    e: React.FormEvent<HTMLFormElement>,
    existingName?: string,
    imageData?: string
  ) {
    e.preventDefault()
    const fd = new FormData(e.currentTarget)
    const data: Record<string, unknown> = {
      item_name: fd.get("item_name") as string,
      quantity: Number(fd.get("quantity")),
      threshold: Number(fd.get("threshold")),
      cost_price: Number(fd.get("cost_price")),
      sale_price: Number(fd.get("sale_price")),
      description: fd.get("description") as string,
    }
    if (imageData) data.image_path = imageData

    try {
      if (existingName) {
        await updateInventoryItem(existingName, data)
        setEditing(null)
        toast("Item updated", "success")
      } else {
        await createInventoryItem(data)
        setShowAdd(false)
        toast("Item added", "success")
      }
      await load()
    } catch {
      toast("Failed to save item", "error")
    }
  }

  function ItemForm({ item, onClose }: { item?: InventoryItem; onClose: () => void }) {
    const [imagePreview, setImagePreview] = useState<string | undefined>(item?.image_path)
    const [imageData, setImageData] = useState<string | undefined>(item?.image_path)
    const fileInputRef = useRef<HTMLInputElement>(null)

    function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
      const file = e.target.files?.[0]
      if (!file) return
      const reader = new FileReader()
      reader.onload = (ev) => {
        const result = ev.target?.result as string
        setImagePreview(result)
        setImageData(result)
      }
      reader.readAsDataURL(file)
    }

    return (
      <form onSubmit={(e) => handleSave(e, item?.item_name, imageData)}>
        <div className="grid grid-cols-2 gap-4 py-4">
          <div className="space-y-1.5">
            <Label>Item Name *</Label>
            <Input name="item_name" required defaultValue={item?.item_name} />
          </div>
          <div className="space-y-1.5">
            <Label>Description</Label>
            <Input name="description" defaultValue={item?.description} />
          </div>
          <div className="space-y-1.5">
            <Label>Quantity</Label>
            <Input name="quantity" type="number" defaultValue={item?.quantity ?? 0} />
          </div>
          <div className="space-y-1.5">
            <Label>Threshold</Label>
            <Input name="threshold" type="number" defaultValue={item?.threshold ?? 0} />
          </div>
          <div className="space-y-1.5">
            <Label>Cost Price ({currency})</Label>
            <Input name="cost_price" type="number" step="0.01" defaultValue={item?.cost_price ?? 0} />
          </div>
          <div className="space-y-1.5">
            <Label>Sale Price ({currency})</Label>
            <Input name="sale_price" type="number" step="0.01" defaultValue={item?.sale_price ?? 0} />
          </div>
          <div className="col-span-2 space-y-1.5">
            <Label>Product Image</Label>
            <div className="flex items-center gap-3">
              {imagePreview && (
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="h-16 w-16 object-cover rounded-lg border border-border"
                />
              )}
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => fileInputRef.current?.click()}
              >
                {imagePreview ? "Change Image" : "Upload Image"}
              </Button>
              {imagePreview && (
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="text-destructive text-xs"
                  onClick={() => { setImagePreview(undefined); setImageData(undefined) }}
                >
                  Remove
                </Button>
              )}
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFileChange}
            />
          </div>
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
          </DialogClose>
          <Button type="submit">Save Item</Button>
        </DialogFooter>
      </form>
    )
  }

  return (
    <div className="space-y-4">
      {showLowStock && (
        <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
          <AlertTriangle className="h-4 w-4 flex-shrink-0" />
          <span className="flex-1 font-medium">Showing low stock items only</span>
          <button
            onClick={() => setShowLowStock(false)}
            className="text-xs underline underline-offset-2 hover:opacity-70"
          >
            Clear filter
          </button>
        </div>
      )}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search items…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <Button onClick={() => setShowAdd(true)} size="sm">
          <Plus className="h-4 w-4 mr-1" /> Add Item
        </Button>
      </div>

      <Dialog open={showAdd} onOpenChange={setShowAdd}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Add Inventory Item</DialogTitle>
          </DialogHeader>
          <ItemForm onClose={() => setShowAdd(false)} />
        </DialogContent>
      </Dialog>

      <Dialog open={!!editing} onOpenChange={(open) => !open && setEditing(null)}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Edit — {editing?.item_name}</DialogTitle>
          </DialogHeader>
          {editing && <ItemForm item={editing} onClose={() => setEditing(null)} />}
        </DialogContent>
      </Dialog>

      {loading ? (
        <p className="text-muted-foreground text-sm py-4">Loading…</p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-12" />
              <SH k="item_name">Name</SH>
              <SH k="quantity" className="text-right">Qty</SH>
              <SH k="cost_price" className="text-right">Cost</SH>
              <SH k="sale_price" className="text-right">Price</SH>
              <TableHead>Category</TableHead>
              <SH k="status">Status</SH>
              <TableHead />
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map((item) => {
              const status = stockStatus(item)
              return (
                <TableRow key={item.id}>
                  <TableCell className="p-2">
                    {item.image_path ? (
                      <img
                        src={item.image_path}
                        alt={item.item_name}
                        className="h-10 w-10 object-cover rounded-md border border-border"
                      />
                    ) : (
                      <div className="h-10 w-10 rounded-md bg-muted flex items-center justify-center">
                        <Package className="h-4 w-4 text-muted-foreground" />
                      </div>
                    )}
                  </TableCell>
                  <TableCell className="font-medium">{item.item_name}</TableCell>
                  <TableCell className="text-right">{item.quantity}</TableCell>
                  <TableCell className="text-right text-muted-foreground text-sm">
                    {currency}{Number(item.cost_price || 0).toFixed(2)}
                  </TableCell>
                  <TableCell className="text-right">
                    {currency}{Number(item.sale_price || 0).toFixed(2)}
                  </TableCell>
                  <TableCell className="text-muted-foreground text-xs">{item.description || "—"}</TableCell>
                  <TableCell>
                    <span
                      className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold"
                      style={{ backgroundColor: status.bg, color: status.color }}
                    >
                      {status.label}
                    </span>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 text-xs text-[#6D28D9]"
                        onClick={() => setEditing(item)}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 text-xs text-destructive"
                        onClick={() => handleDelete(item.item_name)}
                      >
                        Delete
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              )
            })}
            {filtered.length === 0 && (
              <TableRow>
                <TableCell colSpan={8} className="text-center text-muted-foreground italic py-8">
                  No items found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      )}
    </div>
  )
}

// ---- POS Tab ----
function POSTab({ inventory }: { inventory: InventoryItem[] }) {
  const [cart, setCart] = useState<Array<{ item: InventoryItem; qty: number }>>([])
  const currency = useCurrency()

  function addToCart(item: InventoryItem) {
    setCart((prev) => {
      const existing = prev.find((c) => c.item.id === item.id)
      if (existing) return prev.map((c) => (c.item.id === item.id ? { ...c, qty: c.qty + 1 } : c))
      return [...prev, { item, qty: 1 }]
    })
  }

  function removeFromCart(id: string) {
    setCart((prev) => prev.filter((c) => c.item.id !== id))
  }

  const total = cart.reduce((s, c) => s + Number(c.item.sale_price || 0) * c.qty, 0)

  return (
    <div className="flex gap-6">
      <div className="flex-1">
        <h3 className="text-sm font-semibold mb-3">Products</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {inventory
            .filter((i) => i.quantity > 0)
            .map((item) => (
              <button
                key={item.id}
                onClick={() => addToCart(item)}
                className="bg-white border border-border rounded-xl overflow-hidden text-left hover:border-[#6D28D9] hover:shadow-sm transition-all"
              >
                {item.image_path ? (
                  <img
                    src={item.image_path}
                    alt={item.item_name}
                    className="w-full h-28 object-cover"
                  />
                ) : (
                  <div className="w-full h-28 bg-muted flex items-center justify-center">
                    <Package className="h-8 w-8 text-muted-foreground opacity-40" />
                  </div>
                )}
                <div className="p-3">
                  <p className="text-sm font-semibold leading-tight line-clamp-2">{item.item_name}</p>
                  <p className="text-sm font-bold mt-1" style={{ color: "#6D28D9" }}>
                    {currency}{Number(item.sale_price || 0).toFixed(2)}
                  </p>
                  <p className="text-xs text-muted-foreground">Stock: {item.quantity}</p>
                </div>
              </button>
            ))}
          {inventory.length === 0 && (
            <p className="text-muted-foreground text-sm col-span-4">No items available.</p>
          )}
        </div>
      </div>

      <div className="w-64 flex-shrink-0">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <ShoppingCart className="h-4 w-4" /> Cart
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 min-h-32">
              {cart.length === 0 && (
                <p className="text-xs text-muted-foreground italic">Cart is empty</p>
              )}
              {cart.map((c) => (
                <div key={c.item.id} className="flex items-center justify-between text-sm">
                  <span className="truncate flex-1 text-foreground">
                    {c.item.item_name} ×{c.qty}
                  </span>
                  <span className="font-medium ml-2" style={{ color: "#6D28D9" }}>
                    {currency}{(Number(c.item.sale_price || 0) * c.qty).toFixed(2)}
                  </span>
                  <button
                    onClick={() => removeFromCart(c.item.id)}
                    className="ml-2 text-destructive hover:opacity-70 text-xs"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
            <div className="mt-3 border-t border-border pt-3">
              <div className="flex justify-between font-semibold text-sm mb-3">
                <span>Total</span>
                <span style={{ color: "#6D28D9" }}>{currency}{total.toFixed(2)}</span>
              </div>
              <Button
                disabled={cart.length === 0}
                className="w-full"
                onClick={() =>
                  alert(
                    `Checkout: ${currency}${total.toFixed(2)} — Use the desktop app or API for full checkout.`
                  )
                }
              >
                Checkout
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

// ---- Bills Tab ----
function BillsTab() {
  const [sales, setSales] = useState<Sale[]>([])
  const [loading, setLoading] = useState(true)
  const [dateFilter, setDateFilter] = useState("")
  const currency = useCurrency()
  const { sortKey, sortDir, SH } = useSortState<BillSortKey>("sale_date")

  useEffect(() => {
    fetchSales()
      .then((d) => { setSales(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  let filtered = dateFilter ? sales.filter((s) => s.sale_date?.startsWith(dateFilter)) : sales

  if (sortDir !== "none") {
    filtered = [...filtered].sort((a, b) => {
      let cmp = 0
      if (sortKey === "sale_date") cmp = (a.sale_date || "").localeCompare(b.sale_date || "")
      else if (sortKey === "item_name") cmp = (a.item_name || "").localeCompare(b.item_name || "")
      else if (sortKey === "quantity") cmp = a.quantity - b.quantity
      else if (sortKey === "total_amount") cmp = a.total_amount - b.total_amount
      return sortDir === "asc" ? cmp : -cmp
    })
  }

  const total = filtered.reduce((s, r) => s + (r.total_amount || 0), 0)

  function handlePrint(sale: Sale) {
    const w = window.open("", "_blank", "width=400,height=600")
    if (!w) return
    w.document.write(`<!DOCTYPE html>
<html>
<head>
  <title>Receipt</title>
  <style>
    body { font-family: monospace; font-size: 13px; padding: 24px; max-width: 320px; margin: 0 auto; }
    h2 { font-size: 18px; margin-bottom: 4px; }
    .sub { font-size: 11px; color: #666; margin-bottom: 16px; }
    hr { border: none; border-top: 1px dashed #999; margin: 12px 0; }
    .row { display: flex; justify-content: space-between; margin-bottom: 6px; }
    .row span:last-child { font-weight: bold; }
    .total { font-size: 15px; font-weight: bold; }
    .footer { text-align: center; font-size: 11px; color: #666; margin-top: 20px; }
    @media print { button { display: none; } }
  </style>
</head>
<body>
  <h2>BzHub — Receipt</h2>
  <p class="sub">${new Date(sale.sale_date || "").toLocaleString()}</p>
  <hr/>
  <div class="row"><span>Item</span><span>${sale.item_name}</span></div>
  <div class="row"><span>Quantity</span><span>${sale.quantity}</span></div>
  <div class="row"><span>Unit Price</span><span>${currency}${(sale.sale_price || 0).toFixed(2)}</span></div>
  <hr/>
  <div class="row total"><span>Total</span><span>${currency}${(sale.total_amount || 0).toFixed(2)}</span></div>
  <p class="footer">Thank you for your purchase!</p>
  <script>window.onload = function() { window.print(); setTimeout(function(){ window.close(); }, 800); }<\/script>
</body>
</html>`)
    w.document.close()
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <Label className="text-sm text-muted-foreground whitespace-nowrap">Filter by date:</Label>
        <Input
          type="date"
          value={dateFilter}
          onChange={(e) => setDateFilter(e.target.value)}
          className="w-44"
        />
        {dateFilter && (
          <Button variant="ghost" size="sm" onClick={() => setDateFilter("")}>
            Clear
          </Button>
        )}
      </div>

      {loading ? (
        <p className="text-muted-foreground text-sm py-4">Loading…</p>
      ) : (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <SH k="sale_date">Date</SH>
                <SH k="item_name">Item</SH>
                <SH k="quantity" className="text-right">Qty</SH>
                <TableHead className="text-right">Unit Price</TableHead>
                <SH k="total_amount" className="text-right">Total</SH>
                <TableHead>User</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((s) => (
                <TableRow key={s.id}>
                  <TableCell className="text-muted-foreground text-xs">
                    {s.sale_date?.slice(0, 16) || ""}
                  </TableCell>
                  <TableCell className="font-medium">{s.item_name}</TableCell>
                  <TableCell className="text-right">{s.quantity}</TableCell>
                  <TableCell className="text-right">
                    {currency}{(s.sale_price || 0).toFixed(2)}
                  </TableCell>
                  <TableCell className="text-right font-medium">
                    {currency}{(s.total_amount || 0).toFixed(2)}
                  </TableCell>
                  <TableCell className="text-muted-foreground">{s.username}</TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 text-xs"
                      onClick={() => handlePrint(s)}
                    >
                      Print
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {filtered.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-muted-foreground italic py-8">
                    No sales found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
          {filtered.length > 0 && (
            <div className="text-right text-sm font-semibold mt-2">
              Total: {currency}{total.toFixed(2)}{" "}
              <span className="text-muted-foreground font-normal">
                ({filtered.length} transactions)
              </span>
            </div>
          )}
        </>
      )}
    </div>
  )
}

// ---- Main Page ----
function OperationsInner() {
  const searchParams = useSearchParams()
  const lowStockFilter = searchParams.get("filter") === "lowstock"
  const [activeTab, setActiveTab] = useState<Tab>("inventory")
  const [inventory, setInventory] = useState<InventoryItem[]>([])

  useEffect(() => {
    fetchInventory()
      .then(setInventory)
      .catch(() => {})
  }, [])

  const tabs: { key: Tab; label: string; icon: React.ReactNode }[] = [
    { key: "inventory", label: "Inventory", icon: <Package className="h-4 w-4" /> },
    { key: "pos", label: "POS", icon: <ShoppingCart className="h-4 w-4" /> },
    { key: "bills", label: "Bills", icon: <Receipt className="h-4 w-4" /> },
  ]

  return (
    <AppLayout activePage="operations">
      <div className="px-6 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold">Operations</h1>
          <p className="text-sm text-muted-foreground">Inventory, POS, and sales management</p>
        </div>

        <div className="flex gap-1 mb-6 bg-white rounded-xl p-1 shadow-sm w-fit border border-border">
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
            {activeTab === "inventory" && <InventoryTab lowStockOnly={lowStockFilter} />}
            {activeTab === "pos" && <POSTab inventory={inventory} />}
            {activeTab === "bills" && <BillsTab />}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}

export default function OperationsPage() {
  return (
    <Suspense fallback={null}>
      <OperationsInner />
    </Suspense>
  )
}
