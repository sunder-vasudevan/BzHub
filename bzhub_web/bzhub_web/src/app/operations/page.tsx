'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import TopNav from '@/components/TopNav';
import {
  fetchContacts, createContact, updateContact, deleteContact,
  fetchInventory, createInventoryItem, updateInventoryItem, deleteInventoryItem,
  fetchSales, fetchPipeline, createLead, updateLead,
} from '@/lib/api';

type Tab = 'contacts' | 'crm' | 'inventory' | 'pos' | 'bills';

interface Contact {
  id: number;
  name: string;
  company: string;
  email: string;
  phone: string;
  source: string;
  status: string;
}

interface InventoryItem {
  id: number;
  item_name: string;
  quantity: number;
  threshold: number;
  cost_price: number;
  sale_price: number;
  description: string;
}

interface Sale {
  id: number;
  sale_date: string;
  item_name: string;
  quantity: number;
  sale_price: number;
  total_amount: number;
  username: string;
}

const STAGES = ['New', 'Contacted', 'Qualified', 'Proposal', 'Won', 'Lost'];
const STAGE_COLORS: Record<string, string> = {
  New: '#6366F1', Contacted: '#0EA5E9', Qualified: '#F59E0B',
  Proposal: '#8B5CF6', Won: '#10B981', Lost: '#EF4444',
};

// ---- Contacts Sub-page ----
function ContactsPanel() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<Contact | null>(null);
  const [showAdd, setShowAdd] = useState(false);

  const load = useCallback(async () => {
    const c = await fetchContacts(search || undefined).catch(() => []);
    setContacts(c);
    setLoading(false);
  }, [search]);

  useEffect(() => { load(); }, [load]);

  async function handleDelete(id: number) {
    if (!confirm('Delete this contact?')) return;
    await deleteContact(id);
    await load();
  }

  async function handleSave(e: React.FormEvent<HTMLFormElement>, id?: number) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const data = { name: fd.get('name'), company: fd.get('company'), email: fd.get('email'), phone: fd.get('phone'), source: fd.get('source') };
    if (id) { await updateContact(id, data); setEditing(null); }
    else { await createContact(data); setShowAdd(false); }
    await load();
  }

  const inputCls = "w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400";

  function ContactForm({ contact, onCancel }: { contact?: Contact; onCancel: () => void }) {
    return (
      <form onSubmit={e => handleSave(e, contact?.id)} className="space-y-2 p-4 bg-gray-50 rounded-xl mb-4">
        <div className="grid grid-cols-2 gap-2">
          <div><label className="text-xs text-gray-500">Name *</label><input name="name" required defaultValue={contact?.name} className={inputCls} /></div>
          <div><label className="text-xs text-gray-500">Company</label><input name="company" defaultValue={contact?.company} className={inputCls} /></div>
          <div><label className="text-xs text-gray-500">Email</label><input name="email" type="email" defaultValue={contact?.email} className={inputCls} /></div>
          <div><label className="text-xs text-gray-500">Phone</label><input name="phone" defaultValue={contact?.phone} className={inputCls} /></div>
          <div><label className="text-xs text-gray-500">Source</label><input name="source" defaultValue={contact?.source} className={inputCls} /></div>
        </div>
        <div className="flex gap-2 pt-1">
          <button type="submit" className="px-4 py-1.5 bg-purple-700 text-white rounded-lg text-sm">Save</button>
          <button type="button" onClick={onCancel} className="px-4 py-1.5 border border-gray-300 rounded-lg text-sm">Cancel</button>
        </div>
      </form>
    );
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search contacts…" className={inputCls + " max-w-64"} />
        <button onClick={load} className="px-3 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50">Search</button>
        <button onClick={() => setShowAdd(true)} className="px-3 py-2 bg-purple-700 text-white rounded-lg text-sm hover:bg-purple-800">+ Add</button>
      </div>
      {showAdd && <ContactForm onCancel={() => setShowAdd(false)} />}
      {editing && <ContactForm contact={editing} onCancel={() => setEditing(null)} />}
      {loading ? <div className="text-gray-400 text-sm py-4">Loading…</div> : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead><tr className="bg-gray-50">{['Name','Company','Email','Phone','Source','Status',''].map(h => <th key={h} className="text-left px-3 py-2 text-gray-500 font-medium border-b border-gray-200">{h}</th>)}</tr></thead>
            <tbody>
              {contacts.map(c => (
                <tr key={c.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="px-3 py-2 font-medium text-gray-900">{c.name}</td>
                  <td className="px-3 py-2 text-gray-600">{c.company}</td>
                  <td className="px-3 py-2 text-gray-600">{c.email}</td>
                  <td className="px-3 py-2 text-gray-600">{c.phone}</td>
                  <td className="px-3 py-2 text-gray-600">{c.source}</td>
                  <td className="px-3 py-2"><span className={`px-2 py-0.5 rounded-full text-xs ${c.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>{c.status}</span></td>
                  <td className="px-3 py-2">
                    <button onClick={() => setEditing(c)} className="text-xs text-purple-600 hover:underline mr-3">Edit</button>
                    <button onClick={() => handleDelete(c.id)} className="text-xs text-red-500 hover:underline">Delete</button>
                  </td>
                </tr>
              ))}
              {contacts.length === 0 && <tr><td colSpan={7} className="px-3 py-6 text-center text-gray-400 text-sm italic">No contacts found.</td></tr>}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ---- Inventory Sub-page ----
function InventoryPanel() {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [editing, setEditing] = useState<InventoryItem | null>(null);

  const load = useCallback(async () => {
    const d = await fetchInventory().catch(() => []);
    setItems(d);
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  async function handleDelete(name: string) {
    if (!confirm(`Delete "${name}"?`)) return;
    await deleteInventoryItem(name);
    await load();
  }

  async function handleSave(e: React.FormEvent<HTMLFormElement>, existingName?: string) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const data = {
      item_name: fd.get('item_name') as string,
      quantity: Number(fd.get('quantity')),
      threshold: Number(fd.get('threshold')),
      cost_price: Number(fd.get('cost_price')),
      sale_price: Number(fd.get('sale_price')),
      description: fd.get('description') as string,
    };
    if (existingName) { await updateInventoryItem(existingName, data); setEditing(null); }
    else { await createInventoryItem(data); setShowAdd(false); }
    await load();
  }

  const inputCls = "w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400";

  function ItemForm({ item, onCancel }: { item?: InventoryItem; onCancel: () => void }) {
    return (
      <form onSubmit={e => handleSave(e, item?.item_name)} className="space-y-2 p-4 bg-gray-50 rounded-xl mb-4">
        <div className="grid grid-cols-2 gap-2">
          <div><label className="text-xs text-gray-500">Item Name *</label><input name="item_name" required defaultValue={item?.item_name} className={inputCls} /></div>
          <div><label className="text-xs text-gray-500">Description</label><input name="description" defaultValue={item?.description} className={inputCls} /></div>
          <div><label className="text-xs text-gray-500">Quantity</label><input name="quantity" type="number" defaultValue={item?.quantity ?? 0} className={inputCls} /></div>
          <div><label className="text-xs text-gray-500">Threshold</label><input name="threshold" type="number" defaultValue={item?.threshold ?? 0} className={inputCls} /></div>
          <div><label className="text-xs text-gray-500">Cost Price $</label><input name="cost_price" type="number" step="0.01" defaultValue={item?.cost_price ?? 0} className={inputCls} /></div>
          <div><label className="text-xs text-gray-500">Sale Price $</label><input name="sale_price" type="number" step="0.01" defaultValue={item?.sale_price ?? 0} className={inputCls} /></div>
        </div>
        <div className="flex gap-2 pt-1">
          <button type="submit" className="px-4 py-1.5 bg-purple-700 text-white rounded-lg text-sm">Save</button>
          <button type="button" onClick={onCancel} className="px-4 py-1.5 border border-gray-300 rounded-lg text-sm">Cancel</button>
        </div>
      </form>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-gray-700">Inventory Items</h2>
        <button onClick={() => setShowAdd(true)} className="px-3 py-2 bg-purple-700 text-white rounded-lg text-sm hover:bg-purple-800">+ Add Item</button>
      </div>
      {showAdd && <ItemForm onCancel={() => setShowAdd(false)} />}
      {editing && <ItemForm item={editing} onCancel={() => setEditing(null)} />}
      {loading ? <div className="text-gray-400 text-sm py-4">Loading…</div> : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead><tr className="bg-gray-50">{['Item','Qty','Threshold','Cost','Sale Price','',''].map(h=><th key={h} className="text-left px-3 py-2 text-gray-500 font-medium border-b border-gray-200">{h}</th>)}</tr></thead>
            <tbody>
              {items.map(i => (
                <tr key={i.id} className={`border-b border-gray-100 hover:bg-gray-50 ${i.quantity <= i.threshold ? 'bg-red-50' : ''}`}>
                  <td className="px-3 py-2 font-medium text-gray-900">{i.item_name}</td>
                  <td className="px-3 py-2">{i.quantity}</td>
                  <td className="px-3 py-2">{i.threshold}</td>
                  <td className="px-3 py-2">${i.cost_price.toFixed(2)}</td>
                  <td className="px-3 py-2">${i.sale_price.toFixed(2)}</td>
                  <td className="px-3 py-2"><button onClick={() => setEditing(i)} className="text-xs text-purple-600 hover:underline mr-3">Edit</button><button onClick={() => handleDelete(i.item_name)} className="text-xs text-red-500 hover:underline">Delete</button></td>
                </tr>
              ))}
              {items.length === 0 && <tr><td colSpan={6} className="text-center py-6 text-gray-400 text-sm italic">No items.</td></tr>}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ---- Bills Sub-page ----
function BillsPanel() {
  const [sales, setSales] = useState<Sale[]>([]);
  const [loading, setLoading] = useState(true);
  const [dateFilter, setDateFilter] = useState('');

  useEffect(() => {
    fetchSales().then(d => { setSales(d); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const filtered = dateFilter ? sales.filter(s => s.sale_date?.startsWith(dateFilter)) : sales;
  const total = filtered.reduce((s, r) => s + (r.total_amount || 0), 0);

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <label className="text-sm text-gray-500">Filter by date:</label>
        <input type="date" value={dateFilter} onChange={e => setDateFilter(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        {dateFilter && <button onClick={() => setDateFilter('')} className="text-xs text-gray-500 hover:underline">Clear</button>}
      </div>
      {loading ? <div className="text-gray-400 text-sm py-4">Loading…</div> : (
        <>
          <div className="overflow-x-auto mb-3">
            <table className="w-full text-sm border-collapse">
              <thead><tr className="bg-gray-50">{['Date','Item','Qty','Price','Total','User'].map(h=><th key={h} className="text-left px-3 py-2 text-gray-500 font-medium border-b border-gray-200">{h}</th>)}</tr></thead>
              <tbody>
                {filtered.map(s => (
                  <tr key={s.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="px-3 py-2 text-gray-600">{s.sale_date?.slice(0, 16) || ''}</td>
                    <td className="px-3 py-2 font-medium text-gray-900">{s.item_name}</td>
                    <td className="px-3 py-2">{s.quantity}</td>
                    <td className="px-3 py-2">${(s.sale_price || 0).toFixed(2)}</td>
                    <td className="px-3 py-2 font-medium">${(s.total_amount || 0).toFixed(2)}</td>
                    <td className="px-3 py-2 text-gray-500">{s.username}</td>
                  </tr>
                ))}
                {filtered.length === 0 && <tr><td colSpan={6} className="text-center py-6 text-gray-400 text-sm italic">No sales found.</td></tr>}
              </tbody>
            </table>
          </div>
          {filtered.length > 0 && (
            <div className="text-right text-sm font-semibold text-gray-700">
              Total: ${total.toFixed(2)} ({filtered.length} transactions)
            </div>
          )}
        </>
      )}
    </div>
  );
}

// ---- Mini Kanban Sub-page ----
function CRMPanel() {
  const [pipeline, setPipeline] = useState<Record<string, unknown[]>>({});
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    const p = await fetchPipeline().catch(() => ({}));
    setPipeline(p);
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  async function moveLead(id: number, currentStage: string) {
    const idx = STAGES.indexOf(currentStage);
    if (idx < STAGES.length - 1) {
      await updateLead(id, { stage: STAGES[idx + 1] });
      await load();
    }
  }

  interface LeadRow { id: number; title: string; value: number; contact_name: string; owner: string; stage: string }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <p className="text-sm text-gray-500">Kanban pipeline — click the CRM tab for full view</p>
        <button onClick={load} className="text-xs border border-gray-300 px-3 py-1.5 rounded-lg hover:bg-gray-50">Refresh</button>
      </div>
      {loading ? <div className="text-gray-400 text-sm py-4">Loading…</div> : (
        <div className="flex gap-3 overflow-x-auto pb-2">
          {STAGES.map(stage => {
            const leads = (pipeline[stage] || []) as LeadRow[];
            const color = STAGE_COLORS[stage];
            return (
              <div key={stage} className="flex-shrink-0 w-44">
                <div className="rounded-t-lg px-2 py-1.5" style={{ backgroundColor: color }}>
                  <span className="text-white text-xs font-semibold">{stage} ({leads.length})</span>
                </div>
                <div className="bg-gray-50 rounded-b-lg p-1.5 space-y-1.5 min-h-16">
                  {leads.map(l => (
                    <div key={l.id} className="bg-white rounded p-2 shadow-sm border-l-2 text-xs" style={{ borderColor: color }}>
                      <p className="font-medium text-gray-900 leading-tight">{l.title}</p>
                      <p className="text-purple-700 font-bold">${(l.value||0).toFixed(0)}</p>
                      {stage !== STAGES[STAGES.length - 1] && (
                        <button onClick={() => moveLead(l.id, stage)} className="text-xs text-gray-400 hover:text-gray-600 mt-1">Move →</button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ---- POS Sub-page ----
function POSPanel({ inventory }: { inventory: InventoryItem[] }) {
  const [cart, setCart] = useState<Array<{ item: InventoryItem; qty: number }>>([]);

  function addToCart(item: InventoryItem) {
    setCart(prev => {
      const existing = prev.find(c => c.item.id === item.id);
      if (existing) return prev.map(c => c.item.id === item.id ? { ...c, qty: c.qty + 1 } : c);
      return [...prev, { item, qty: 1 }];
    });
  }

  function removeFromCart(id: number) {
    setCart(prev => prev.filter(c => c.item.id !== id));
  }

  const total = cart.reduce((s, c) => s + c.item.sale_price * c.qty, 0);

  return (
    <div className="flex gap-6">
      <div className="flex-1">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Products</h3>
        <div className="grid grid-cols-3 gap-3">
          {inventory.filter(i => i.quantity > 0).map(item => (
            <button key={item.id} onClick={() => addToCart(item)}
              className="bg-white border border-gray-200 rounded-xl p-3 text-left hover:border-purple-400 hover:shadow-sm transition-all">
              <p className="text-sm font-semibold text-gray-900 leading-tight">{item.item_name}</p>
              <p className="text-sm font-bold text-purple-700 mt-1">${item.sale_price.toFixed(2)}</p>
              <p className="text-xs text-gray-400">Stock: {item.quantity}</p>
            </button>
          ))}
          {inventory.length === 0 && <p className="text-gray-400 text-sm col-span-3">No items available.</p>}
        </div>
      </div>
      <div className="w-64 flex-shrink-0">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Cart</h3>
        <div className="bg-gray-50 rounded-xl p-3 space-y-2 min-h-32">
          {cart.length === 0 && <p className="text-xs text-gray-400 italic">Cart is empty</p>}
          {cart.map(c => (
            <div key={c.item.id} className="flex items-center justify-between text-sm">
              <span className="truncate flex-1 text-gray-800">{c.item.item_name} x{c.qty}</span>
              <span className="text-purple-700 font-medium ml-2">${(c.item.sale_price * c.qty).toFixed(2)}</span>
              <button onClick={() => removeFromCart(c.item.id)} className="ml-2 text-red-400 hover:text-red-600 text-xs">&times;</button>
            </div>
          ))}
        </div>
        <div className="mt-3 border-t border-gray-200 pt-3">
          <div className="flex justify-between font-semibold text-sm mb-3">
            <span>Total</span>
            <span className="text-purple-700">${total.toFixed(2)}</span>
          </div>
          <button
            disabled={cart.length === 0}
            className="w-full bg-purple-700 hover:bg-purple-800 disabled:opacity-50 text-white font-medium py-2 rounded-lg text-sm transition-colors"
            onClick={() => { alert(`Checkout: $${total.toFixed(2)} — Use the desktop app or API for full checkout.`); }}
          >
            Checkout
          </button>
        </div>
      </div>
    </div>
  );
}

// ---- Main Operations Page ----
export default function OperationsPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<Tab>('contacts');
  const [inventory, setInventory] = useState<InventoryItem[]>([]);

  useEffect(() => {
    if (!localStorage.getItem('bzhub_user')) { router.push('/'); return; }
    fetchInventory().then(setInventory).catch(() => {});
  }, [router]);

  const tabs: { key: Tab; label: string }[] = [
    { key: 'contacts', label: 'Contacts' },
    { key: 'crm', label: 'CRM Pipeline' },
    { key: 'inventory', label: 'Inventory' },
    { key: 'pos', label: 'POS' },
    { key: 'bills', label: 'Bills' },
  ];

  return (
    <div className="min-h-screen bg-surface">
      <TopNav active="operations" />
      <main className="max-w-7xl mx-auto px-6 py-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Operations</h1>

        {/* Tab Bar */}
        <div className="flex gap-1 mb-6 bg-white rounded-xl p-1 shadow-sm w-fit">
          {tabs.map(t => (
            <button
              key={t.key}
              onClick={() => setActiveTab(t.key)}
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                activeTab === t.key
                  ? 'bg-purple-700 text-white'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          {activeTab === 'contacts' && <ContactsPanel />}
          {activeTab === 'crm' && <CRMPanel />}
          {activeTab === 'inventory' && <InventoryPanel />}
          {activeTab === 'pos' && <POSPanel inventory={inventory} />}
          {activeTab === 'bills' && <BillsPanel />}
        </div>
      </main>
    </div>
  );
}
