"use client"

import { useEffect, useState, useCallback } from "react"
import AppLayout from "@/components/layout/AppLayout"
import { toast } from "@/components/ui/toast"
import { useCurrency } from "@/hooks/useCurrency"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
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
import { Plus, Search, ShoppingCart, Package, Receipt } from "lucide-react"

type Tab = "inventory" | "pos" | "bills"

interface InventoryItem {
  id: number
  item_name: string
  quantity: number
  threshold: number
  cost_price: number
  sale_price: number
  description: string
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

// ---- Inventory Tab ----
function InventoryTab() {
  const [items, setItems] = useState<InventoryItem[]>([])
  const [filtered, setFiltered] = useState<InventoryItem[]>([])
  const [search, setSearch] = useState("")
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [editing, setEditing] = useState<InventoryItem | null>(null)
  const currency = useCurrency()

  const load = useCallback(async () => {
    const d = await fetchInventory().catch(() => [])
    setItems(d)
    setFiltered(d)
    setLoading(false)
  }, [])

  useEffect(() => {
    load()
  }, [load])

  useEffect(() => {
    const q = search.toLowerCase()
    setFiltered(
      q
        ? items.filter(
            (i) =>
              i.item_name.toLowerCase().includes(q) ||
              (i.description || "").toLowerCase().includes(q)
          )
        : items
    )
  }, [search, items])

  async function handleDelete(name: string) {
    if (!confirm(`Delete "${name}"?`)) return
    try {
      await deleteInventoryItem(name)
      await load()
      toast("Item deleted", "success")
    } catch {
      toast("Failed to save item", "error")
    }
  }

  async function handleSave(e: React.FormEvent<HTMLFormElement>, existingName?: string) {
    e.preventDefault()
    const fd = new FormData(e.currentTarget)
    const data = {
      item_name: fd.get("item_name") as string,
      quantity: Number(fd.get("quantity")),
      threshold: Number(fd.get("threshold")),
      cost_price: Number(fd.get("cost_price")),
      sale_price: Number(fd.get("sale_price")),
      description: fd.get("description") as string,
    }
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

  function stockStatus(item: InventoryItem): { label: string; variant: "default" | "secondary" | "destructive" | "outline" } {
    if (item.quantity === 0) return { label: "Out of Stock", variant: "destructive" }
    if (item.quantity <= item.threshold) return { label: "Low Stock", variant: "outline" }
    return { label: "In Stock", variant: "secondary" }
  }

  function ItemForm({ item, onClose }: { item?: InventoryItem; onClose: () => void }) {
    return (
      <form onSubmit={(e) => handleSave(e, item?.item_name)}>
        <div className="grid grid-cols-2 gap-4 py-4">
          <div className="space-y-1.5">
            <Label htmlFor="item_name">Item Name *</Label>
            <Input name="item_name" required defaultValue={item?.item_name} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="description">Description</Label>
            <Input name="description" defaultValue={item?.description} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="quantity">Quantity</Label>
            <Input name="quantity" type="number" defaultValue={item?.quantity ?? 0} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="threshold">Threshold</Label>
            <Input name="threshold" type="number" defaultValue={item?.threshold ?? 0} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="cost_price">Cost Price ($)</Label>
            <Input name="cost_price" type="number" step="0.01" defaultValue={item?.cost_price ?? 0} />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="sale_price">Sale Price ($)</Label>
            <Input name="sale_price" type="number" step="0.01" defaultValue={item?.sale_price ?? 0} />
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

      {/* Add dialog */}
      <Dialog open={showAdd} onOpenChange={setShowAdd}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Inventory Item</DialogTitle>
          </DialogHeader>
          <ItemForm onClose={() => setShowAdd(false)} />
        </DialogContent>
      </Dialog>

      {/* Edit dialog */}
      <Dialog open={!!editing} onOpenChange={(open) => !open && setEditing(null)}>
        <DialogContent>
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
              <TableHead>Name</TableHead>
              <TableHead className="text-right">Qty</TableHead>
              <TableHead className="text-right">Price</TableHead>
              <TableHead>Category</TableHead>
              <TableHead>Status</TableHead>
              <TableHead />
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.map((item) => {
              const status = stockStatus(item)
              return (
                <TableRow key={item.id}>
                  <TableCell className="font-medium">{item.item_name}</TableCell>
                  <TableCell className="text-right">{item.quantity}</TableCell>
                  <TableCell className="text-right">{currency}{Number(item.sale_price || 0).toFixed(2)}</TableCell>
                  <TableCell className="text-muted-foreground text-xs">{item.description || "—"}</TableCell>
                  <TableCell>
                    <Badge variant={status.variant}>{status.label}</Badge>
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
                <TableCell colSpan={6} className="text-center text-muted-foreground italic py-8">
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

  function removeFromCart(id: number) {
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
                className="bg-white border border-border rounded-xl p-3 text-left hover:border-[#6D28D9] hover:shadow-sm transition-all"
              >
                <p className="text-sm font-semibold leading-tight">{item.item_name}</p>
                <p className="text-sm font-bold mt-1" style={{ color: "#6D28D9" }}>
                  {currency}{Number(item.sale_price || 0).toFixed(2)}
                </p>
                <p className="text-xs text-muted-foreground">Stock: {item.quantity}</p>
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
                    {c.item.item_name} x{c.qty}
                  </span>
                  <span className="font-medium ml-2" style={{ color: "#6D28D9" }}>
                    {currency}{(Number(c.item.sale_price || 0) * c.qty).toFixed(2)}
                  </span>
                  <button
                    onClick={() => removeFromCart(c.item.id)}
                    className="ml-2 text-destructive hover:opacity-70 text-xs"
                  >
                    &times;
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

  useEffect(() => {
    fetchSales()
      .then((d) => {
        setSales(d)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  const filtered = dateFilter ? sales.filter((s) => s.sale_date?.startsWith(dateFilter)) : sales
  const total = filtered.reduce((s, r) => s + (r.total_amount || 0), 0)

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
                <TableHead>Date</TableHead>
                <TableHead>Item</TableHead>
                <TableHead className="text-right">Qty</TableHead>
                <TableHead className="text-right">Price</TableHead>
                <TableHead className="text-right">Total</TableHead>
                <TableHead>User</TableHead>
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
                  <TableCell className="text-right">{currency}{(s.sale_price || 0).toFixed(2)}</TableCell>
                  <TableCell className="text-right font-medium">
                    {currency}{(s.total_amount || 0).toFixed(2)}
                  </TableCell>
                  <TableCell className="text-muted-foreground">{s.username}</TableCell>
                </TableRow>
              ))}
              {filtered.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center text-muted-foreground italic py-8">
                    No sales found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
          {filtered.length > 0 && (
            <div className="text-right text-sm font-semibold">
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
export default function OperationsPage() {
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

        {/* Tab Bar */}
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
              style={
                activeTab === t.key
                  ? { backgroundColor: "#6D28D9" }
                  : undefined
              }
            >
              {t.icon}
              {t.label}
            </button>
          ))}
        </div>

        <Card>
          <CardContent className="p-6">
            {activeTab === "inventory" && <InventoryTab />}
            {activeTab === "pos" && <POSTab inventory={inventory} />}
            {activeTab === "bills" && <BillsTab />}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
