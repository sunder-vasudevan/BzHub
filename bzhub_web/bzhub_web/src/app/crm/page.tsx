"use client"

import { useEffect, useState, useCallback } from "react"
import AppLayout from "@/components/layout/AppLayout"
import { toast } from "@/components/ui/toast"
import { useCurrency } from "@/hooks/useCurrency"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { fetchPipeline, createLead, updateLead, deleteLead, fetchContacts } from "@/lib/db"
import { Plus, RefreshCw, TrendingUp, DollarSign, Users, Pencil, List, LayoutGrid, Filter } from "lucide-react"

const STAGES = ["New", "Contacted", "Qualified", "Proposal", "Won", "Lost"] as const
type Stage = (typeof STAGES)[number]
type View = "list" | "kanban" | "funnel"

const STAGE_CONFIG: Record<Stage, { color: string; textColor: string; bg: string }> = {
  New:       { color: "#6366F1", textColor: "#4338CA", bg: "#EEF2FF" },
  Contacted: { color: "#0EA5E9", textColor: "#0369A1", bg: "#E0F2FE" },
  Qualified: { color: "#F59E0B", textColor: "#B45309", bg: "#FEF3C7" },
  Proposal:  { color: "#8B5CF6", textColor: "#6D28D9", bg: "#EDE9FE" },
  Won:       { color: "#10B981", textColor: "#047857", bg: "#D1FAE5" },
  Lost:      { color: "#EF4444", textColor: "#B91C1C", bg: "#FEE2E2" },
}

interface Lead {
  id: number
  contact_id: number | null
  title: string
  stage: string
  value: number
  probability: number
  owner: string
  notes: string
  contact_name: string | null
}

interface Contact {
  id: number
  name: string
  company: string
}

const LOCAL_STORAGE_KEY = "bzhub_crm_view"

export default function CRMPage() {
  const [pipeline, setPipeline] = useState<Record<string, Lead[]>>({})
  const [contacts, setContacts] = useState<Contact[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [addContactId, setAddContactId] = useState<string>("none")
  const [addStage, setAddStage] = useState<Stage>("New")
  const [editStage, setEditStage] = useState<string>("")
  const [stageFilter, setStageFilter] = useState<Stage | "All">("All")
  const [updatingId, setUpdatingId] = useState<number | null>(null)
  const [view, setView] = useState<View>("list")
  const [expandedFunnelStage, setExpandedFunnelStage] = useState<Stage | null>(null)
  const currency = useCurrency()

  // Persist view to localStorage
  useEffect(() => {
    const saved = localStorage.getItem(LOCAL_STORAGE_KEY)
    if (saved === "list" || saved === "kanban" || saved === "funnel") {
      setView(saved)
    }
  }, [])

  function switchView(v: View) {
    setView(v)
    localStorage.setItem(LOCAL_STORAGE_KEY, v)
  }

  const loadData = useCallback(async () => {
    try {
      const [p, c] = await Promise.all([fetchPipeline(), fetchContacts()])
      setPipeline(p)
      setContacts(c)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadData() }, [loadData])
  useEffect(() => { if (selectedLead) setEditStage(selectedLead.stage) }, [selectedLead])

  const allLeads = Object.values(pipeline).flat()
  const filteredLeads = stageFilter === "All" ? allLeads : (pipeline[stageFilter] ?? [])

  const totalValue = allLeads.filter(l => l.stage !== "Lost").reduce((s, l) => s + (l.value || 0), 0)
  const won = pipeline["Won"]?.length || 0
  const closed = won + (pipeline["Lost"]?.length || 0)
  const convRate = closed > 0 ? Math.round((won / closed) * 100) : 0

  async function handleStageChange(lead: Lead, newStage: string) {
    setUpdatingId(lead.id)
    try {
      await updateLead(lead.id, { stage: newStage })
      await loadData()
      toast(`Moved to ${newStage}`, "success")
    } catch {
      toast("Failed to update stage", "error")
    } finally {
      setUpdatingId(null)
    }
  }

  async function handleDeleteLead(id: number) {
    if (!confirm("Delete this lead?")) return
    await deleteLead(id)
    setSelectedLead(null)
    await loadData()
    toast("Lead deleted", "success")
  }

  async function handleAddLead(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const fd = new FormData(e.currentTarget)
    const title = fd.get("title") as string
    if (!title) return
    await createLead({
      title,
      stage: addStage,
      contact_id: addContactId !== "none" ? Number(addContactId) : null,
      value: Number(fd.get("value") || 0),
      probability: Number(fd.get("probability") || 0),
      owner: fd.get("owner") as string || "",
      notes: fd.get("notes") as string || "",
    })
    setShowAddModal(false)
    setAddContactId("none")
    setAddStage("New")
    await loadData()
    toast("Lead added", "success")
  }

  async function handleSaveLead(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (!selectedLead) return
    const fd = new FormData(e.currentTarget)
    await updateLead(selectedLead.id, {
      title: fd.get("title") as string,
      stage: editStage,
      value: Number(fd.get("value") || 0),
      probability: Number(fd.get("probability") || 0),
      owner: fd.get("owner") as string || "",
      notes: fd.get("notes") as string || "",
    })
    setSelectedLead(null)
    await loadData()
    toast("Lead saved", "success")
  }

  // ── View toggle button helper ──────────────────────────────────────────────
  function ViewBtn({ v, icon: Icon, label }: { v: View; icon: React.ElementType; label: string }) {
    const active = view === v
    return (
      <button
        onClick={() => switchView(v)}
        title={label}
        className="flex items-center justify-center h-8 w-8 rounded-md border transition-all"
        style={active
          ? { backgroundColor: "var(--brand-color)", borderColor: "var(--brand-color)", color: "#fff" }
          : { backgroundColor: "transparent", borderColor: "#e2e8f0", color: "#64748b" }
        }
      >
        <Icon className="h-4 w-4" />
      </button>
    )
  }

  // ── Kanban view ────────────────────────────────────────────────────────────
  function KanbanView() {
    return (
      <div className="flex gap-4 overflow-x-auto pb-4">
        {STAGES.map((stage) => {
          const cfg = STAGE_CONFIG[stage]
          const leads = pipeline[stage] ?? []
          return (
            <div key={stage} className="flex-shrink-0 w-64">
              {/* Column header */}
              <div
                className="flex items-center justify-between px-3 py-2 rounded-t-lg mb-0"
                style={{ backgroundColor: cfg.color }}
              >
                <div className="flex items-center gap-2">
                  <span className="text-white text-sm font-semibold">{stage}</span>
                  <span className="text-white/80 text-xs font-medium bg-white/20 rounded-full px-1.5 py-0.5">
                    {leads.length}
                  </span>
                </div>
                <button
                  onClick={() => { setAddStage(stage); setShowAddModal(true) }}
                  className="text-white/90 hover:text-white hover:bg-white/20 rounded p-0.5 transition-colors"
                  title={`Add lead to ${stage}`}
                >
                  <Plus className="h-4 w-4" />
                </button>
              </div>

              {/* Cards */}
              <div className="space-y-2 bg-muted/30 rounded-b-lg p-2 min-h-[120px]">
                {leads.map((lead) => (
                  <div
                    key={lead.id}
                    className="bg-background rounded-lg p-3 shadow-sm border border-border cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => setSelectedLead(lead)}
                  >
                    <p className="text-sm font-medium leading-tight mb-1">{lead.title}</p>
                    {lead.contact_name && (
                      <p className="text-xs text-muted-foreground mb-2">{lead.contact_name}</p>
                    )}
                    <div className="flex items-center justify-between gap-2">
                      {lead.value > 0 ? (
                        <span
                          className="text-xs font-semibold px-2 py-0.5 rounded-full"
                          style={{ backgroundColor: cfg.bg, color: cfg.textColor }}
                        >
                          {currency}{lead.value.toLocaleString("en-US", { minimumFractionDigits: 0 })}
                        </span>
                      ) : (
                        <span />
                      )}
                      {lead.owner && (
                        <span className="text-xs text-muted-foreground truncate max-w-[80px]">{lead.owner}</span>
                      )}
                    </div>
                  </div>
                ))}
                {leads.length === 0 && (
                  <p className="text-xs text-muted-foreground text-center py-4">No leads</p>
                )}
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  // ── Funnel view ────────────────────────────────────────────────────────────
  function FunnelView() {
    const funnelStages: Stage[] = ["New", "Contacted", "Qualified", "Proposal"]
    const outcomeStages: Stage[] = ["Won", "Lost"]

    const maxCount = Math.max(1, ...funnelStages.map(s => (pipeline[s] ?? []).length))

    return (
      <div className="space-y-6">
        {/* Funnel bars */}
        <Card>
          <CardContent className="p-4 space-y-3">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-4">Pipeline Funnel</p>
            {funnelStages.map((stage) => {
              const cfg = STAGE_CONFIG[stage]
              const leads = pipeline[stage] ?? []
              const stageValue = leads.reduce((s, l) => s + (l.value || 0), 0)
              const widthPct = maxCount > 0 ? Math.round((leads.length / maxCount) * 100) : 0
              const isExpanded = expandedFunnelStage === stage

              return (
                <div key={stage}>
                  <button
                    className="w-full text-left"
                    onClick={() => setExpandedFunnelStage(isExpanded ? null : stage)}
                  >
                    <div className="flex items-center gap-3 mb-1">
                      <span className="text-sm font-medium w-24 shrink-0">{stage}</span>
                      <div className="flex-1 bg-muted rounded-full h-6 overflow-hidden">
                        <div
                          className="h-full rounded-full flex items-center px-2 transition-all duration-500"
                          style={{ width: `${widthPct}%`, backgroundColor: cfg.color, minWidth: leads.length > 0 ? "2rem" : "0" }}
                        >
                          {leads.length > 0 && (
                            <span className="text-white text-xs font-semibold">{leads.length}</span>
                          )}
                        </div>
                      </div>
                      <span className="text-sm font-semibold w-24 text-right shrink-0">
                        {stageValue > 0 ? `${currency}${stageValue.toLocaleString("en-US", { minimumFractionDigits: 0 })}` : "—"}
                      </span>
                      <span className="text-xs text-muted-foreground w-4 shrink-0">{isExpanded ? "▲" : "▼"}</span>
                    </div>
                  </button>

                  {/* Expanded leads */}
                  {isExpanded && leads.length > 0 && (
                    <div className="ml-28 mb-2 space-y-1">
                      {leads.map((lead) => (
                        <div
                          key={lead.id}
                          className="flex items-center justify-between px-3 py-1.5 rounded-md cursor-pointer hover:bg-muted/60 transition-colors text-sm border border-border"
                          onClick={() => setSelectedLead(lead)}
                        >
                          <span className="font-medium">{lead.title}</span>
                          {lead.value > 0 && (
                            <span className="text-xs font-semibold" style={{ color: cfg.textColor }}>
                              {currency}{lead.value.toLocaleString("en-US", { minimumFractionDigits: 0 })}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                  {isExpanded && leads.length === 0 && (
                    <p className="ml-28 mb-2 text-xs text-muted-foreground">No leads in this stage.</p>
                  )}
                </div>
              )
            })}
          </CardContent>
        </Card>

        {/* Outcome cards */}
        <div>
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">Outcomes</p>
          <div className="grid grid-cols-2 gap-4">
            {outcomeStages.map((stage) => {
              const cfg = STAGE_CONFIG[stage]
              const leads = pipeline[stage] ?? []
              const stageValue = leads.reduce((s, l) => s + (l.value || 0), 0)
              const isExpanded = expandedFunnelStage === stage

              return (
                <Card key={stage} className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setExpandedFunnelStage(isExpanded ? null : stage)}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-semibold" style={{ color: cfg.textColor }}>{stage}</span>
                      <span
                        className="text-xs font-bold px-2 py-0.5 rounded-full"
                        style={{ backgroundColor: cfg.bg, color: cfg.textColor }}
                      >
                        {leads.length}
                      </span>
                    </div>
                    <p className="text-lg font-bold">
                      {stageValue > 0 ? `${currency}${stageValue.toLocaleString("en-US", { minimumFractionDigits: 0 })}` : "—"}
                    </p>
                    {isExpanded && leads.length > 0 && (
                      <div className="mt-3 space-y-1 border-t border-border pt-2">
                        {leads.map((lead) => (
                          <div
                            key={lead.id}
                            className="flex items-center justify-between text-xs cursor-pointer hover:bg-muted/60 rounded px-1 py-0.5"
                            onClick={(e) => { e.stopPropagation(); setSelectedLead(lead) }}
                          >
                            <span className="font-medium">{lead.title}</span>
                            {lead.value > 0 && (
                              <span style={{ color: cfg.textColor }}>
                                {currency}{lead.value.toLocaleString("en-US", { minimumFractionDigits: 0 })}
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      </div>
    )
  }

  return (
    <AppLayout activePage="crm">
      <div className="px-4 py-4 md:px-6 md:py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold">CRM Pipeline</h1>
            <p className="text-sm text-muted-foreground">
              {allLeads.length} leads
            </p>
          </div>
          <div className="flex items-center gap-2">
            {/* View switcher */}
            <div className="flex items-center gap-1 mr-1">
              <ViewBtn v="list" icon={List} label="List view" />
              <ViewBtn v="kanban" icon={LayoutGrid} label="Kanban view" />
              <ViewBtn v="funnel" icon={Filter} label="Funnel view" />
            </div>
            <Button variant="outline" size="sm" onClick={loadData} disabled={loading}>
              <RefreshCw className="h-4 w-4 mr-1" /> Refresh
            </Button>
            <Button size="sm" onClick={() => setShowAddModal(true)} style={{ backgroundColor: "var(--brand-color)" }} className="text-white hover:opacity-90">
              <Plus className="h-4 w-4 mr-1" /> Add Lead
            </Button>
          </div>
        </div>

        {/* Stats bar */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="h-9 w-9 rounded-lg flex items-center justify-center" style={{ backgroundColor: "var(--brand-color)20" }}>
                <DollarSign className="h-4 w-4" style={{ color: "var(--brand-color)" }} />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Pipeline Value</p>
                <p className="text-lg font-bold">{currency}{totalValue.toLocaleString("en-US", { minimumFractionDigits: 0 })}</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="h-9 w-9 rounded-lg flex items-center justify-center bg-emerald-100">
                <TrendingUp className="h-4 w-4 text-emerald-600" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Conversion Rate</p>
                <p className="text-lg font-bold">{convRate}%</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="h-9 w-9 rounded-lg flex items-center justify-center bg-blue-100">
                <Users className="h-4 w-4 text-blue-600" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Total Leads</p>
                <p className="text-lg font-bold">{allLeads.length}</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-destructive/10 border border-destructive/20 text-destructive rounded-lg text-sm">{error}</div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="h-8 w-8 rounded-full border-4 border-t-transparent animate-spin"
              style={{ borderColor: "var(--brand-color)", borderTopColor: "transparent" }} />
          </div>
        ) : view === "kanban" ? (
          <KanbanView />
        ) : view === "funnel" ? (
          <FunnelView />
        ) : (
          <>
            {/* Stage filter pills — list view only */}
            <div className="flex flex-wrap items-center gap-2 mb-4">
              {(["All", ...STAGES] as const).map((s) => {
                const isActive = stageFilter === s
                const cfg = s !== "All" ? STAGE_CONFIG[s] : null
                const count = s === "All" ? allLeads.length : (pipeline[s]?.length ?? 0)
                return (
                  <button
                    key={s}
                    onClick={() => setStageFilter(s as Stage | "All")}
                    className="px-3 py-1 rounded-full text-xs font-medium border transition-all"
                    style={isActive && cfg
                      ? { backgroundColor: cfg.bg, borderColor: cfg.color, color: cfg.textColor }
                      : isActive
                      ? { backgroundColor: "var(--brand-color)", borderColor: "var(--brand-color)", color: "#fff" }
                      : { backgroundColor: "transparent", borderColor: "#e2e8f0", color: "#64748b" }
                    }
                  >
                    {s} <span className="opacity-70">({count})</span>
                  </button>
                )
              })}
            </div>

            {filteredLeads.length === 0 ? (
              <div className="text-center py-16 text-muted-foreground text-sm">No leads found.</div>
            ) : (
              /* Table */
              <Card>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wide">Lead</th>
                        <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wide">Stage</th>
                        <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wide">Contact</th>
                        <th className="text-right px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wide">Value</th>
                        <th className="text-right px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wide">Prob.</th>
                        <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wide">Owner</th>
                        <th className="px-4 py-3" />
                      </tr>
                    </thead>
                    <tbody>
                      {filteredLeads.map((lead) => {
                        const cfg = STAGE_CONFIG[lead.stage as Stage] ?? STAGE_CONFIG["New"]
                        return (
                          <tr key={lead.id} className="border-b border-border last:border-0 hover:bg-muted/40 transition-colors">
                            <td className="px-4 py-3">
                              <span className="font-medium">{lead.title}</span>
                            </td>
                            <td className="px-4 py-3">
                              <select
                                value={lead.stage}
                                disabled={updatingId === lead.id}
                                onChange={(e) => handleStageChange(lead, e.target.value)}
                                className="text-xs font-medium rounded-full px-2.5 py-1 border-0 cursor-pointer focus:outline-none focus:ring-1 focus:ring-ring disabled:opacity-50"
                                style={{ backgroundColor: cfg.bg, color: cfg.textColor }}
                              >
                                {STAGES.map(s => (
                                  <option key={s} value={s}>{s}</option>
                                ))}
                              </select>
                            </td>
                            <td className="px-4 py-3 text-muted-foreground">{lead.contact_name || "—"}</td>
                            <td className="px-4 py-3 text-right font-medium">
                              {lead.value > 0 ? `${currency}${lead.value.toLocaleString("en-US", { minimumFractionDigits: 0 })}` : "—"}
                            </td>
                            <td className="px-4 py-3 text-right text-muted-foreground">
                              {lead.probability > 0 ? `${lead.probability}%` : "—"}
                            </td>
                            <td className="px-4 py-3 text-muted-foreground">{lead.owner || "—"}</td>
                            <td className="px-4 py-3 text-right">
                              <Button variant="ghost" size="sm" className="h-7 w-7 p-0" onClick={() => setSelectedLead(lead)}>
                                <Pencil className="h-3.5 w-3.5" />
                              </Button>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </Card>
            )}
          </>
        )}
      </div>

      {/* Lead Detail / Edit Modal */}
      <Dialog open={!!selectedLead} onOpenChange={(open) => !open && setSelectedLead(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Edit Lead</DialogTitle>
          </DialogHeader>
          {selectedLead && (
            <form onSubmit={handleSaveLead} className="space-y-3">
              <div className="space-y-1.5">
                <Label htmlFor="edit-title">Title *</Label>
                <Input id="edit-title" name="title" defaultValue={selectedLead.title} required />
              </div>
              <div className="space-y-1.5">
                <Label>Stage</Label>
                <Select value={editStage} onValueChange={setEditStage}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {STAGES.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label htmlFor="edit-value">Value</Label>
                  <Input id="edit-value" name="value" type="number" step="0.01" defaultValue={selectedLead.value || 0} />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="edit-prob">Probability (%)</Label>
                  <Input id="edit-prob" name="probability" type="number" min="0" max="100" defaultValue={selectedLead.probability || 0} />
                </div>
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="edit-owner">Owner</Label>
                <Input id="edit-owner" name="owner" defaultValue={selectedLead.owner || ""} />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="edit-notes">Notes</Label>
                <textarea
                  id="edit-notes"
                  name="notes"
                  defaultValue={selectedLead.notes || ""}
                  rows={3}
                  className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                />
              </div>
              <DialogFooter className="gap-2 pt-2">
                <Button type="button" variant="destructive" size="sm" onClick={() => handleDeleteLead(selectedLead.id)}>Delete</Button>
                <DialogClose asChild><Button type="button" variant="outline" size="sm">Cancel</Button></DialogClose>
                <Button type="submit" size="sm" style={{ backgroundColor: "var(--brand-color)" }} className="text-white hover:opacity-90">Save</Button>
              </DialogFooter>
            </form>
          )}
        </DialogContent>
      </Dialog>

      {/* Add Lead Modal */}
      <Dialog open={showAddModal} onOpenChange={(open) => { if (!open) { setShowAddModal(false); setAddContactId("none"); setAddStage("New") } }}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Add Lead</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleAddLead} className="space-y-3">
            <div className="space-y-1.5">
              <Label htmlFor="add-title">Title *</Label>
              <Input id="add-title" name="title" required autoFocus />
            </div>
            <div className="space-y-1.5">
              <Label>Stage</Label>
              <Select value={addStage} onValueChange={(v) => setAddStage(v as Stage)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {STAGES.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>Contact</Label>
              <Select value={addContactId} onValueChange={setAddContactId}>
                <SelectTrigger><SelectValue placeholder="(none)" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">(none)</SelectItem>
                  {contacts.map((c) => (
                    <SelectItem key={c.id} value={String(c.id)}>
                      {c.name}{c.company ? ` (${c.company})` : ""}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label htmlFor="add-value">Value</Label>
                <Input id="add-value" name="value" type="number" step="0.01" defaultValue="0" />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="add-prob">Probability (%)</Label>
                <Input id="add-prob" name="probability" type="number" min="0" max="100" defaultValue="0" />
              </div>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="add-owner">Owner</Label>
              <Input id="add-owner" name="owner" />
            </div>
            <DialogFooter className="pt-2">
              <DialogClose asChild><Button type="button" variant="outline">Cancel</Button></DialogClose>
              <Button type="submit" style={{ backgroundColor: "var(--brand-color)" }} className="text-white hover:opacity-90">Add Lead</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </AppLayout>
  )
}
