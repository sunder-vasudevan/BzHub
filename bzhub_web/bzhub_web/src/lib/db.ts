/**
 * db.ts — Supabase data layer
 * Drop-in replacement for api.ts — all pages import from here.
 */
import { supabase } from './supabase'

// ---- Inventory ----

export async function fetchInventory() {
  const { data, error } = await supabase
    .from('inventory')
    .select('*')
    .order('item_name')
  if (error) throw new Error(error.message)
  return data ?? []
}

export async function createInventoryItem(item: Record<string, unknown>) {
  const { error } = await supabase.from('inventory').insert([item])
  if (error) throw new Error(error.message)
}

export async function updateInventoryItem(itemName: string, updates: Record<string, unknown>) {
  const { error } = await supabase
    .from('inventory')
    .update(updates)
    .eq('item_name', itemName)
  if (error) throw new Error(error.message)
}

export async function deleteInventoryItem(itemName: string) {
  const { error } = await supabase
    .from('inventory')
    .delete()
    .eq('item_name', itemName)
  if (error) throw new Error(error.message)
}

// ---- Sales ----

export async function fetchSales() {
  const { data, error } = await supabase
    .from('sales')
    .select('*')
    .order('sale_date', { ascending: false })
  if (error) throw new Error(error.message)
  return data ?? []
}

export async function createSale(sale: Record<string, unknown>) {
  const { error } = await supabase.from('sales').insert([sale])
  if (error) throw new Error(error.message)
}

// ---- CRM Contacts ----

export async function fetchContacts(search?: string) {
  let q = supabase.from('crm_contacts').select('*').order('name')
  if (search) q = q.ilike('name', `%${search}%`)
  const { data, error } = await q
  if (error) throw new Error(error.message)
  return data ?? []
}

export async function createContact(item: Record<string, unknown>) {
  const { error } = await supabase.from('crm_contacts').insert([item])
  if (error) throw new Error(error.message)
}

export async function updateContact(id: number, updates: Record<string, unknown>) {
  const { error } = await supabase.from('crm_contacts').update(updates).eq('id', id)
  if (error) throw new Error(error.message)
}

export async function deleteContact(id: number) {
  const { error } = await supabase.from('crm_contacts').delete().eq('id', id)
  if (error) throw new Error(error.message)
}

// ---- CRM Leads ----

export async function fetchLeads(stage?: string) {
  let q = supabase.from('crm_leads').select('*').order('created_at', { ascending: false })
  if (stage) q = q.eq('stage', stage)
  const { data, error } = await q
  if (error) throw new Error(error.message)
  return data ?? []
}

export async function fetchPipeline() {
  const { data, error } = await supabase
    .from('crm_leads')
    .select('stage, value')
  if (error) throw new Error(error.message)
  // Group by stage
  const stages: Record<string, { count: number; value: number }> = {}
  for (const row of data ?? []) {
    if (!stages[row.stage]) stages[row.stage] = { count: 0, value: 0 }
    stages[row.stage].count++
    stages[row.stage].value += row.value ?? 0
  }
  return stages
}

export async function createLead(item: Record<string, unknown>) {
  const { error } = await supabase.from('crm_leads').insert([item])
  if (error) throw new Error(error.message)
}

export async function updateLead(id: number, updates: Record<string, unknown>) {
  const { error } = await supabase.from('crm_leads').update(updates).eq('id', id)
  if (error) throw new Error(error.message)
}

export async function deleteLead(id: number) {
  const { error } = await supabase.from('crm_leads').delete().eq('id', id)
  if (error) throw new Error(error.message)
}

// ---- Employees ----

export async function fetchEmployees() {
  const { data, error } = await supabase
    .from('employees')
    .select('*')
    .order('name')
  if (error) throw new Error(error.message)
  return data ?? []
}

export async function createEmployee(item: Record<string, unknown>) {
  const { error } = await supabase.from('employees').insert([item])
  if (error) throw new Error(error.message)
}

export async function updateEmployee(id: number, updates: Record<string, unknown>) {
  const { error } = await supabase.from('employees').update(updates).eq('id', id)
  if (error) throw new Error(error.message)
}

export async function deleteEmployee(id: number) {
  const { error } = await supabase.from('employees').delete().eq('id', id)
  if (error) throw new Error(error.message)
}

// ---- Payroll ----

export async function fetchPayrolls() {
  const { data, error } = await supabase
    .from('payroll')
    .select('*')
    .order('created_at', { ascending: false })
  if (error) throw new Error(error.message)
  return data ?? []
}

// ---- Company Settings ----

export async function fetchCompanySettings() {
  const { data, error } = await supabase
    .from('company_info')
    .select('*')
    .limit(1)
    .single()
  if (error && error.code !== 'PGRST116') throw new Error(error.message)
  return data ?? {}
}

export async function saveCompanySettings(updates: Record<string, unknown>) {
  // upsert into id=1 row
  const { error } = await supabase
    .from('company_info')
    .upsert([{ id: 1, ...updates }])
  if (error) throw new Error(error.message)
}

// ---- Dashboard KPIs ----

export async function fetchKPIs() {
  const [invRes, salesRes, leadsRes] = await Promise.all([
    supabase.from('inventory').select('quantity, threshold, cost_price'),
    supabase.from('sales').select('total_amount, sale_date'),
    supabase.from('crm_leads').select('value, stage'),
  ])

  const inventory = invRes.data ?? []
  const sales = salesRes.data ?? []
  const leads = leadsRes.data ?? []

  const today = new Date().toISOString().slice(0, 10)
  const todaySales = sales.filter((s) => (s.sale_date ?? '').startsWith(today))
  const today_sales = todaySales.reduce((s, r) => s + (r.total_amount ?? 0), 0)

  const inventory_value = inventory.reduce(
    (s, r) => s + (r.quantity ?? 0) * (r.cost_price ?? 0), 0
  )
  const low_stock_count = inventory.filter(
    (r) => (r.threshold ?? 0) > 0 && (r.quantity ?? 0) <= (r.threshold ?? 0)
  ).length

  const allTotal = sales.reduce((s, r) => s + (r.total_amount ?? 0), 0)
  const days = Math.max(new Set(sales.map((s) => (s.sale_date ?? '').slice(0, 10))).size, 1)
  const avg_daily_sales = allTotal / days

  const now = new Date()
  const weekAgo = new Date(now.getTime() - 7 * 86400000).toISOString().slice(0, 10)
  const twoWeeksAgo = new Date(now.getTime() - 14 * 86400000).toISOString().slice(0, 10)
  const weekTotal = sales
    .filter((s) => (s.sale_date ?? '') >= weekAgo)
    .reduce((s, r) => s + (r.total_amount ?? 0), 0)
  const priorTotal = sales
    .filter((s) => (s.sale_date ?? '') >= twoWeeksAgo && (s.sale_date ?? '') < weekAgo)
    .reduce((s, r) => s + (r.total_amount ?? 0), 0)
  const growth_pct = priorTotal > 0 ? Math.round(((weekTotal - priorTotal) / priorTotal) * 1000) / 10 : 0

  const pipeline_value = leads
    .filter((l) => !['Won', 'Lost'].includes(l.stage))
    .reduce((s, r) => s + (r.value ?? 0), 0)
  const won = leads.filter((l) => l.stage === 'Won').length
  const conversion_rate = leads.length > 0 ? Math.round((won / leads.length) * 100) : 0

  return {
    today_sales: Math.round(today_sales * 100) / 100,
    inventory_value: Math.round(inventory_value * 100) / 100,
    low_stock_count,
    total_items: inventory.length,
    avg_daily_sales: Math.round(avg_daily_sales * 100) / 100,
    growth_pct,
    pipeline_value: Math.round(pipeline_value * 100) / 100,
    conversion_rate,
  }
}

// ---- Dashboard Trend ----

export async function fetchTrend(days = 30) {
  const start = new Date(Date.now() - days * 86400000).toISOString().slice(0, 10)
  const { data, error } = await supabase
    .from('sales')
    .select('sale_date, total_amount')
    .gte('sale_date', start)
    .order('sale_date')
  if (error) throw new Error(error.message)

  // Group by date
  const map: Record<string, number> = {}
  for (const row of data ?? []) {
    const d = (row.sale_date ?? '').slice(0, 10)
    map[d] = (map[d] ?? 0) + (row.total_amount ?? 0)
  }
  return Object.entries(map).map(([date, total]) => ({ date, total: Math.round(total * 100) / 100 }))
}

// ---- Dashboard Product Velocity ----

export async function fetchProductVelocity(days = 30) {
  const start = new Date(Date.now() - days * 86400000).toISOString().slice(0, 10)
  const { data, error } = await supabase
    .from('sales')
    .select('item_name, quantity, total_amount')
    .gte('sale_date', start)
  if (error) throw new Error(error.message)

  const map: Record<string, { qty: number; total: number }> = {}
  for (const row of data ?? []) {
    if (!map[row.item_name]) map[row.item_name] = { qty: 0, total: 0 }
    map[row.item_name].qty += row.quantity ?? 0
    map[row.item_name].total += row.total_amount ?? 0
  }
  const sorted = Object.entries(map)
    .map(([item_name, v]) => ({ item_name, qty_sold: v.qty, total: Math.round(v.total * 100) / 100 }))
    .sort((a, b) => b.qty_sold - a.qty_sold)

  return {
    fast: sorted.slice(0, 5),
    slow: sorted.slice(-5).reverse(),
  }
}

// ---- Health ----

export async function fetchHealth() {
  return { status: 'ok', source: 'supabase' }
}
