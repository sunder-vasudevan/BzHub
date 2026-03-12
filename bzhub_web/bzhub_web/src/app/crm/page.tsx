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
import { Plus, RefreshCw, TrendingUp, DollarSign, Users, Pencil } from "lucide-react"

const STAGES = ["New", "Contacted", "Qualified", "Proposal", "Won", "Lost"] as const
type Stage = (typeof STAGES)[number]

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
  const currency = useCurrency()

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

        {/* Stage filter pills */}
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

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="h-8 w-8 rounded-full border-4 border-t-transparent animate-spin"
              style={{ borderColor: "var(--brand-color)", borderTopColor: "transparent" }} />
          </div>
        ) : filteredLeads.length === 0 ? (
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
