/**
 * BizHub API client — connects to the FastAPI backend.
 *
 * Set NEXT_PUBLIC_API_URL in .env.local to override the default.
 * Default: http://localhost:8000
 */
const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export async function apiFetch(path: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

// ---- Auth ----

export async function login(username: string, password: string) {
  return apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
}

// ---- Dashboard ----

export async function fetchKPIs() {
  return apiFetch('/dashboard/kpis');
}

export async function fetchTrend(days = 30) {
  return apiFetch(`/dashboard/trend?days=${days}`);
}

// ---- Inventory ----

export async function fetchInventory() {
  return apiFetch('/inventory');
}

export async function createInventoryItem(data: Record<string, unknown>) {
  return apiFetch('/inventory', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateInventoryItem(itemName: string, data: Record<string, unknown>) {
  return apiFetch(`/inventory/${encodeURIComponent(itemName)}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteInventoryItem(itemName: string) {
  return apiFetch(`/inventory/${encodeURIComponent(itemName)}`, {
    method: 'DELETE',
  });
}

// ---- Contacts ----

export async function fetchContacts(search?: string) {
  const qs = search ? `?search=${encodeURIComponent(search)}` : '';
  return apiFetch(`/contacts${qs}`);
}

export async function createContact(data: Record<string, unknown>) {
  return apiFetch('/contacts', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateContact(id: number, data: Record<string, unknown>) {
  return apiFetch(`/contacts/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteContact(id: number) {
  return apiFetch(`/contacts/${id}`, { method: 'DELETE' });
}

// ---- Leads ----

export async function fetchLeads(stage?: string) {
  const qs = stage ? `?stage=${encodeURIComponent(stage)}` : '';
  return apiFetch(`/leads${qs}`);
}

export async function fetchPipeline() {
  return apiFetch('/leads/pipeline');
}

export async function createLead(data: Record<string, unknown>) {
  return apiFetch('/leads', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateLead(id: number, data: Record<string, unknown>) {
  return apiFetch(`/leads/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteLead(id: number) {
  return apiFetch(`/leads/${id}`, { method: 'DELETE' });
}

// ---- Sales ----

export async function fetchSales() {
  return apiFetch('/sales');
}
