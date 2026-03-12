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
    .select('*')
    .order('created_at', { ascending: false })
  if (error) throw new Error(error.message)
  // Group leads by stage — matches CRM page's Record<string, Lead[]> shape
  const stages: Record<string, unknown[]> = {}
  for (const row of data ?? []) {
    const s: string = row.stage ?? 'New'
    if (!stages[s]) stages[s] = []
    stages[s].push(row)
  }
  return stages as Record<string, never[]>
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
  const { data, error } = await supabase.from('employees').insert([item]).select('id').single()
  if (error) throw new Error(error.message)
  logAudit({ table_name: 'employees', record_id: String(data?.id ?? ''), action: 'create', summary: `Created employee: ${item.name ?? ''}` })
}

export async function updateEmployee(id: number, updates: Record<string, unknown>) {
  const { error } = await supabase.from('employees').update(updates).eq('id', id)
  if (error) throw new Error(error.message)
}

export async function deleteEmployee(id: number) {
  const { error } = await supabase.from('employees').delete().eq('id', id)
  if (error) throw new Error(error.message)
  logAudit({ table_name: 'employees', record_id: String(id), action: 'delete', summary: `Deleted employee id ${id}` })
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

// ---- Suppliers ----

export async function fetchSuppliers() {
  const { data, error } = await supabase
    .from('suppliers')
    .select('*')
    .order('name')
  if (error) throw new Error(error.message)
  return data ?? []
}

export async function createSupplier(item: Record<string, unknown>) {
  const { error } = await supabase.from('suppliers').insert([item])
  if (error) throw new Error(error.message)
}

export async function updateSupplier(id: number, updates: Record<string, unknown>) {
  const { error } = await supabase.from('suppliers').update(updates).eq('id', id)
  if (error) throw new Error(error.message)
}

export async function deleteSupplier(id: number) {
  const { error } = await supabase.from('suppliers').delete().eq('id', id)
  if (error) throw new Error(error.message)
}

// ---- Goals ----

export interface Goal {
  id: number
  employee_id: number
  employee_name?: string
  title: string
  description?: string
  due_date?: string
  status: string
}

export async function fetchGoals(): Promise<Goal[]> {
  const { data, error } = await supabase
    .from('goals')
    .select('*, employees(name)')
    .order('id', { ascending: false })
  if (error) throw new Error(error.message)
  return (data ?? []).map((row: Record<string, unknown>) => {
    const emp = row.employees as { name?: string } | null
    return {
      id: row.id as number,
      employee_id: row.employee_id as number,
      employee_name: emp?.name,
      title: row.title as string,
      description: row.description as string | undefined,
      due_date: row.due_date as string | undefined,
      status: (row.status as string) ?? 'Draft',
    }
  })
}

export async function createGoal(data: {
  employee_id: number
  title: string
  description: string
  due_date: string
  status: string
}): Promise<void> {
  const { data: inserted, error } = await supabase.from('goals').insert([data]).select('id').single()
  if (error) throw new Error(error.message)
  logAudit({ table_name: 'goals', record_id: String(inserted?.id ?? ''), action: 'create', summary: `Goal created: ${data.title}` })
}

export async function updateGoal(
  id: number,
  data: Partial<{ title: string; description: string; due_date: string; status: string }>
): Promise<void> {
  const { error } = await supabase.from('goals').update(data).eq('id', id)
  if (error) throw new Error(error.message)
}

export async function deleteGoal(id: number): Promise<void> {
  const { error } = await supabase.from('goals').delete().eq('id', id)
  if (error) throw new Error(error.message)
  logAudit({ table_name: 'goals', record_id: String(id), action: 'delete', summary: `Deleted goal id ${id}` })
}

export async function createGoalCheckin(data: {
  goal_id: number
  progress_pct: number
  notes: string
  checked_by: string
}): Promise<void> {
  const { error } = await supabase.from('goal_checkins').insert([data])
  if (error) throw new Error(error.message)
}

// ---- Appraisals ----

export interface Appraisal {
  id: number
  employee_id: number
  employee_name?: string
  period: string
  self_rating: number
  manager_rating: number
  self_comments?: string
  manager_comments?: string
  status: string
}

export async function fetchAppraisals(): Promise<Appraisal[]> {
  const { data, error } = await supabase
    .from('appraisals')
    .select('*, employees(name)')
    .order('id', { ascending: false })
  if (error) throw new Error(error.message)
  return (data ?? []).map((row: Record<string, unknown>) => {
    const emp = row.employees as { name?: string } | null
    return {
      id: row.id as number,
      employee_id: row.employee_id as number,
      employee_name: emp?.name,
      period: row.period as string,
      self_rating: (row.self_rating as number) ?? 0,
      manager_rating: (row.manager_rating as number) ?? 0,
      self_comments: row.self_comments as string | undefined,
      manager_comments: row.manager_comments as string | undefined,
      status: (row.status as string) ?? 'Pending',
    }
  })
}

export async function createAppraisal(data: {
  employee_id: number
  period: string
  self_rating: number
  manager_rating: number
  self_comments: string
  manager_comments: string
  status: string
}): Promise<void> {
  const { error } = await supabase.from('appraisals').insert([data])
  if (error) throw new Error(error.message)
}

export async function updateAppraisal(
  id: number,
  data: Partial<{
    period: string
    self_rating: number
    manager_rating: number
    self_comments: string
    manager_comments: string
    status: string
  }>
): Promise<void> {
  const { error } = await supabase.from('appraisals').update(data).eq('id', id)
  if (error) throw new Error(error.message)
}

export async function deleteAppraisal(id: number): Promise<void> {
  const { error } = await supabase.from('appraisals').delete().eq('id', id)
  if (error) throw new Error(error.message)
}

// ---- Skills ----

export interface Skill {
  id: number
  name: string
  category: string
}

export interface EmployeeSkill {
  id: number
  employee_id: number
  skill_id: number
  proficiency: string
  skill_name?: string
  skill_category?: string
}

export async function fetchSkills(): Promise<Skill[]> {
  const { data, error } = await supabase
    .from('skills')
    .select('*')
    .order('category')
  if (error) throw new Error(error.message)
  return data ?? []
}

export async function createSkill(data: { name: string; category: string }): Promise<void> {
  const { error } = await supabase.from('skills').insert([data])
  if (error) throw new Error(error.message)
}

export async function fetchEmployeeSkills(employeeId: number): Promise<EmployeeSkill[]> {
  const { data, error } = await supabase
    .from('employee_skills')
    .select('*, skills(name, category)')
    .eq('employee_id', employeeId)
  if (error) throw new Error(error.message)
  return (data ?? []).map((row: Record<string, unknown>) => {
    const skill = row.skills as { name?: string; category?: string } | null
    return {
      id: row.id as number,
      employee_id: row.employee_id as number,
      skill_id: row.skill_id as number,
      proficiency: row.proficiency as string,
      skill_name: skill?.name,
      skill_category: skill?.category,
    }
  })
}

export async function addEmployeeSkill(data: {
  employee_id: number
  skill_id: number
  proficiency: string
}): Promise<void> {
  const { error } = await supabase.from('employee_skills').insert([data])
  if (error) throw new Error(error.message)
}

export async function updateEmployeeSkill(id: number, proficiency: string): Promise<void> {
  const { error } = await supabase.from('employee_skills').update({ proficiency }).eq('id', id)
  if (error) throw new Error(error.message)
}

export async function deleteEmployeeSkill(id: number): Promise<void> {
  const { error } = await supabase.from('employee_skills').delete().eq('id', id)
  if (error) throw new Error(error.message)
}

// ---- Leave Requests ----

export interface LeaveRequest {
  id: number
  employee_id: number
  employee_name?: string
  leave_type: string
  start_date: string
  end_date: string
  reason?: string
  status: string
  reviewed_by?: string
  reviewed_at?: string
  created_at?: string
}

export async function fetchLeaveRequests(): Promise<LeaveRequest[]> {
  const { data, error } = await supabase
    .from('leave_requests')
    .select('*, employees(name)')
    .order('created_at', { ascending: false })
  if (error) throw new Error(error.message)
  return (data ?? []).map((row: Record<string, unknown>) => {
    const emp = row.employees as { name?: string } | null
    return {
      id: row.id as number,
      employee_id: row.employee_id as number,
      employee_name: emp?.name,
      leave_type: (row.leave_type as string) ?? 'Annual',
      start_date: row.start_date as string,
      end_date: row.end_date as string,
      reason: row.reason as string | undefined,
      status: (row.status as string) ?? 'Pending',
      reviewed_by: row.reviewed_by as string | undefined,
      reviewed_at: row.reviewed_at as string | undefined,
      created_at: row.created_at as string | undefined,
    }
  })
}

export async function createLeaveRequest(data: {
  employee_id: number
  leave_type: string
  start_date: string
  end_date: string
  reason: string
}): Promise<void> {
  const { data: inserted, error } = await supabase.from('leave_requests').insert([{ ...data, status: 'Pending' }]).select('id').single()
  if (error) throw new Error(error.message)
  logAudit({ table_name: 'leave_requests', record_id: String(inserted?.id ?? ''), action: 'create', summary: `Leave request: ${data.leave_type} for employee ${data.employee_id}` })
}

export async function updateLeaveRequestStatus(
  id: number,
  status: 'Approved' | 'Rejected',
  reviewed_by = 'Manager'
): Promise<void> {
  const { error } = await supabase
    .from('leave_requests')
    .update({ status, reviewed_by, reviewed_at: new Date().toISOString() })
    .eq('id', id)
  if (error) throw new Error(error.message)
  logAudit({ table_name: 'leave_requests', record_id: String(id), action: 'update', summary: `Leave request ${status.toLowerCase()} by ${reviewed_by}` })
}

export async function deleteLeaveRequest(id: number): Promise<void> {
  const { error } = await supabase.from('leave_requests').delete().eq('id', id)
  if (error) throw new Error(error.message)
  logAudit({ table_name: 'leave_requests', record_id: String(id), action: 'delete', summary: `Deleted leave request id ${id}` })
}

// ---- Purchase Orders ----

export interface PurchaseOrder {
  id: number
  supplier_id?: number
  supplier_name?: string
  order_date?: string
  expected_delivery?: string
  total_amount: number
  notes?: string
  status: string
  reviewed_by?: string
  reviewed_at?: string
  created_at?: string
}

export async function fetchPurchaseOrders(): Promise<PurchaseOrder[]> {
  const { data, error } = await supabase
    .from('purchase_orders')
    .select('*')
    .order('created_at', { ascending: false })
  if (error) throw new Error(error.message)
  return (data ?? []).map((row: Record<string, unknown>) => ({
    id: row.id as number,
    supplier_id: row.supplier_id as number | undefined,
    supplier_name: row.supplier_name as string | undefined,
    order_date: row.order_date as string | undefined,
    expected_delivery: row.expected_delivery as string | undefined,
    total_amount: (row.total_amount as number) ?? 0,
    notes: row.notes as string | undefined,
    status: (row.status as string) ?? 'Pending',
    reviewed_by: row.reviewed_by as string | undefined,
    reviewed_at: row.reviewed_at as string | undefined,
    created_at: row.created_at as string | undefined,
  }))
}

export async function createPurchaseOrder(data: {
  supplier_id?: number
  supplier_name?: string
  order_date: string
  expected_delivery: string
  total_amount: number
  notes: string
}): Promise<void> {
  const { data: inserted, error } = await supabase.from('purchase_orders').insert([{ ...data, status: 'Pending' }]).select('id').single()
  if (error) throw new Error(error.message)
  logAudit({ table_name: 'purchase_orders', record_id: String(inserted?.id ?? ''), action: 'create', summary: `PO created: ${data.supplier_name ?? 'supplier'} amount ${data.total_amount}` })
}

export async function updatePurchaseOrderStatus(
  id: number,
  status: 'Approved' | 'Rejected' | 'Ordered' | 'Delivered',
  reviewed_by = 'Manager'
): Promise<void> {
  const { error } = await supabase
    .from('purchase_orders')
    .update({ status, reviewed_by, reviewed_at: new Date().toISOString() })
    .eq('id', id)
  if (error) throw new Error(error.message)
  logAudit({ table_name: 'purchase_orders', record_id: String(id), action: 'update', summary: `PO status → ${status} by ${reviewed_by}` })
}

export async function deletePurchaseOrder(id: number): Promise<void> {
  const { error } = await supabase.from('purchase_orders').delete().eq('id', id)
  if (error) throw new Error(error.message)
  logAudit({ table_name: 'purchase_orders', record_id: String(id), action: 'delete', summary: `Deleted PO id ${id}` })
}

// ---- Audit Log ----

export interface AuditLog {
  id: number
  table_name: string
  record_id: string
  action: string
  changed_by: string
  summary: string
  created_at: string
}

export async function logAudit(data: {
  table_name: string
  record_id: string
  action: 'create' | 'update' | 'delete'
  changed_by?: string
  summary?: string
}): Promise<void> {
  // fire-and-forget — never throw, audit failures shouldn't block UX
  supabase.from('audit_logs').insert([{ ...data, changed_by: data.changed_by ?? 'admin' }]).then(() => {})
}

export async function fetchAuditLogs(limit = 100): Promise<AuditLog[]> {
  const { data, error } = await supabase
    .from('audit_logs')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(limit)
  if (error) throw new Error(error.message)
  return data ?? []
}

// ---- Auth (simple hardcoded for now — replace with Supabase Auth later) ----

export async function login(username: string, password: string) {
  // Temporary: accept admin/admin123 locally; replace with Supabase Auth when ready
  if (username === 'admin' && password === 'admin123') {
    return { user: 'admin', role: 'admin', token: 'local' }
  }
  throw new Error('401 Invalid credentials')
}

// ---- Health ----

export async function fetchHealth() {
  return { status: 'ok', source: 'supabase' }
}
