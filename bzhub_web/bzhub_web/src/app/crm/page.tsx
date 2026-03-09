'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import TopNav from '@/components/TopNav';
import { fetchPipeline, createLead, updateLead, deleteLead, fetchContacts } from '@/lib/api';

const STAGES = ['New', 'Contacted', 'Qualified', 'Proposal', 'Won', 'Lost'];

const STAGE_COLORS: Record<string, string> = {
  New: '#6366F1',
  Contacted: '#0EA5E9',
  Qualified: '#F59E0B',
  Proposal: '#8B5CF6',
  Won: '#10B981',
  Lost: '#EF4444',
};

interface Lead {
  id: number;
  contact_id: number | null;
  title: string;
  stage: string;
  value: number;
  probability: number;
  owner: string;
  notes: string;
  contact_name: string | null;
}

interface Contact {
  id: number;
  name: string;
  company: string;
}

export default function CRMPage() {
  const router = useRouter();
  const [pipeline, setPipeline] = useState<Record<string, Lead[]>>({});
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [showAddModal, setShowAddModal] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [p, c] = await Promise.all([fetchPipeline(), fetchContacts()]);
      setPipeline(p);
      setContacts(c);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!localStorage.getItem('bzhub_user')) { router.push('/'); return; }
    loadData();
  }, [router, loadData]);

  async function moveLead(lead: Lead) {
    const idx = STAGES.indexOf(lead.stage);
    if (idx < STAGES.length - 1) {
      await updateLead(lead.id, { stage: STAGES[idx + 1] });
      await loadData();
    }
  }

  async function handleDeleteLead(id: number) {
    if (!confirm('Delete this lead?')) return;
    await deleteLead(id);
    setSelectedLead(null);
    await loadData();
  }

  async function handleAddLead(stage: string, formData: FormData) {
    const title = formData.get('title') as string;
    if (!title) return;
    const contactId = formData.get('contact_id');
    await createLead({
      title,
      stage,
      contact_id: contactId ? Number(contactId) : null,
      value: Number(formData.get('value') || 0),
      probability: Number(formData.get('probability') || 0),
      owner: formData.get('owner') as string || '',
      notes: formData.get('notes') as string || '',
    });
    setShowAddModal(null);
    await loadData();
  }

  async function handleSaveLead(lead: Lead, formData: FormData) {
    await updateLead(lead.id, {
      title: formData.get('title') as string,
      stage: formData.get('stage') as string,
      value: Number(formData.get('value') || 0),
      probability: Number(formData.get('probability') || 0),
      owner: formData.get('owner') as string || '',
      notes: formData.get('notes') as string || '',
    });
    setSelectedLead(null);
    await loadData();
  }

  const totalLeads = Object.values(pipeline).flat().length;
  const totalValue = Object.values(pipeline).flat()
    .filter(l => l.stage !== 'Lost')
    .reduce((s, l) => s + (l.value || 0), 0);
  const won = pipeline['Won']?.length || 0;
  const closed = (pipeline['Won']?.length || 0) + (pipeline['Lost']?.length || 0);
  const convRate = closed > 0 ? Math.round((won / closed) * 100) : 0;

  return (
    <div className="min-h-screen bg-surface">
      <TopNav active="crm" />
      <main className="px-6 py-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">CRM Pipeline</h1>
            <p className="text-sm text-gray-500">
              {totalLeads} leads &middot; Pipeline: ${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2 })} &middot; Conversion: {convRate}%
            </p>
          </div>
          <button
            onClick={loadData}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Refresh
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm border border-red-200">
            {error}
          </div>
        )}

        {loading ? (
          <div className="text-center py-20 text-gray-400">Loading pipeline…</div>
        ) : (
          <div className="flex gap-4 overflow-x-auto pb-4">
            {STAGES.map(stage => {
              const leads = pipeline[stage] || [];
              const color = STAGE_COLORS[stage];
              return (
                <div key={stage} className="flex-shrink-0 w-60">
                  {/* Column header */}
                  <div
                    className="rounded-t-xl px-3 py-2 flex items-center justify-between"
                    style={{ backgroundColor: color }}
                  >
                    <span className="text-white font-semibold text-sm">
                      {stage} <span className="opacity-75">({leads.length})</span>
                    </span>
                    <button
                      onClick={() => setShowAddModal(stage)}
                      className="text-white text-lg leading-none hover:opacity-75 transition-opacity"
                      title={`Add lead to ${stage}`}
                    >
                      +
                    </button>
                  </div>

                  {/* Cards */}
                  <div className="bg-gray-50 rounded-b-xl min-h-24 p-2 space-y-2">
                    {leads.length === 0 && (
                      <p className="text-xs text-gray-400 italic text-center py-3">No leads</p>
                    )}
                    {leads.map(lead => (
                      <div
                        key={lead.id}
                        className="bg-white rounded-lg shadow-sm p-3 cursor-pointer hover:shadow-md transition-shadow border-l-4"
                        style={{ borderColor: color }}
                        onClick={() => setSelectedLead(lead)}
                      >
                        <p className="text-sm font-semibold text-gray-900 leading-tight mb-1">{lead.title}</p>
                        {lead.contact_name && (
                          <p className="text-xs text-gray-500 mb-1">👤 {lead.contact_name}</p>
                        )}
                        <p className="text-sm font-bold" style={{ color }}>
                          ${(lead.value || 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                        </p>
                        {lead.owner && <p className="text-xs text-gray-400">Owner: {lead.owner}</p>}
                        {stage !== STAGES[STAGES.length - 1] && (
                          <button
                            onClick={e => { e.stopPropagation(); moveLead(lead); }}
                            className="mt-2 text-xs px-2 py-0.5 border border-gray-300 rounded hover:bg-gray-50 transition-colors"
                          >
                            Move →
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>

      {/* Lead Detail Modal */}
      {selectedLead && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-gray-900">Lead Detail</h2>
                <button onClick={() => setSelectedLead(null)} className="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
              </div>
              <form
                onSubmit={async e => {
                  e.preventDefault();
                  await handleSaveLead(selectedLead, new FormData(e.currentTarget));
                }}
                className="space-y-3"
              >
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Title *</label>
                  <input name="title" defaultValue={selectedLead.title} required
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Stage</label>
                  <select name="stage" defaultValue={selectedLead.stage}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400">
                    {STAGES.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
                <div className="flex gap-3">
                  <div className="flex-1">
                    <label className="block text-xs font-medium text-gray-600 mb-1">Value $</label>
                    <input name="value" type="number" step="0.01" defaultValue={selectedLead.value || 0}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400" />
                  </div>
                  <div className="flex-1">
                    <label className="block text-xs font-medium text-gray-600 mb-1">Prob %</label>
                    <input name="probability" type="number" min="0" max="100" defaultValue={selectedLead.probability || 0}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400" />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Owner</label>
                  <input name="owner" defaultValue={selectedLead.owner || ''}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Notes</label>
                  <textarea name="notes" defaultValue={selectedLead.notes || ''} rows={3}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400" />
                </div>
                <div className="flex gap-2 pt-2">
                  <button type="submit"
                    className="flex-1 bg-purple-700 hover:bg-purple-800 text-white font-medium py-2 rounded-lg text-sm transition-colors">
                    Save
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDeleteLead(selectedLead.id)}
                    className="px-4 py-2 bg-red-50 hover:bg-red-100 text-red-600 font-medium rounded-lg text-sm transition-colors">
                    Delete
                  </button>
                  <button type="button" onClick={() => setSelectedLead(null)}
                    className="px-4 py-2 border border-gray-300 hover:bg-gray-50 rounded-lg text-sm transition-colors">
                    Close
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Add Lead Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-gray-900">Add Lead — {showAddModal}</h2>
                <button onClick={() => setShowAddModal(null)} className="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
              </div>
              <form
                onSubmit={async e => {
                  e.preventDefault();
                  await handleAddLead(showAddModal, new FormData(e.currentTarget));
                }}
                className="space-y-3"
              >
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Title *</label>
                  <input name="title" required
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Contact</label>
                  <select name="contact_id"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-400">
                    <option value="">(none)</option>
                    {contacts.map(c => (
                      <option key={c.id} value={c.id}>{c.name}{c.company ? ` (${c.company})` : ''}</option>
                    ))}
                  </select>
                </div>
                <div className="flex gap-3">
                  <div className="flex-1">
                    <label className="block text-xs font-medium text-gray-600 mb-1">Value $</label>
                    <input name="value" type="number" step="0.01" defaultValue="0"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
                  </div>
                  <div className="flex-1">
                    <label className="block text-xs font-medium text-gray-600 mb-1">Prob %</label>
                    <input name="probability" type="number" min="0" max="100" defaultValue="0"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-600 mb-1">Owner</label>
                  <input name="owner"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
                </div>
                <div className="flex gap-2 pt-2">
                  <button type="submit"
                    className="flex-1 bg-purple-700 hover:bg-purple-800 text-white font-medium py-2 rounded-lg text-sm transition-colors">
                    Add Lead
                  </button>
                  <button type="button" onClick={() => setShowAddModal(null)}
                    className="px-4 py-2 border border-gray-300 hover:bg-gray-50 rounded-lg text-sm transition-colors">
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
