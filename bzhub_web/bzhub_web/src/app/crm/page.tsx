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
import { Plus, RefreshCw, TrendingUp, DollarSign } from "lucide-react"

const STAGES = ["New", "Contacted", "Qualified", "Proposal", "Won", "Lost"] as const
type Stage = (typeof STAGES)[number]

const STAGE_CONFIG: Record<Stage, { color: string; bg: string }> = {
  New:       { color: "#6366F1", bg: "#EEF2FF" },
  Contacted: { color: "#0EA5E9", bg: "#E0F2FE" },
  Qualified: { color: "#F59E0B", bg: "#FEF3C7" },
  Proposal:  { color: "#8B5CF6", bg: "#EDE9FE" },
  Won:       { color: "#10B981", bg: "#D1FAE5" },
  Lost:      { color: "#EF4444", bg: "#FEE2E2" },
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

function stageBadgeVariant(stage: string): "default" | "secondary" | "destructive" | "outline" {
  if (stage === "Won") return "default"
  if (stage === "Lost") return "destructive"
  return "secondary"
}

export default function CRMPage() {
  const [pipeline, setPipeline] = useState<Record<string, Lead[]>>({})
  const [contacts, setContacts] = useState<Contact[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null)
  const [showAddModal, setShowAddModal] = useState<Stage | null>(null)
  // controlled select state for add/edit forms
  const [addContactId, setAddContactId] = useState<string>("none")
  const [editStage, setEditStage] = useState<string>("")
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

  useEffect(() => {
    loadData()
  }, [loadData])

  useEffect(() => {
    if (selectedLead) setEditStage(selectedLead.stage)
  }, [selectedLead])

  async function moveLead(lead: Lead) {
    const idx = STAGES.indexOf(lead.stage as Stage)
    if (idx < STAGES.length - 1) {
      await updateLead(lead.id, { stage: STAGES[idx + 1] })
      await loadData()
    }
  }

  async function handleDeleteLead(id: number) {
    if (!confirm("Delete this lead?")) return
    await deleteLead(id)
    setSelectedLead(null)
    await loadData()
  }

  async function handleAddLead(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (!showAddModal) return
    const fd = new FormData(e.currentTarget)
    const title = fd.get("title") as string
    if (!title) return
    await createLead({
      title,
      stage: showAddModal,
      contact_id: addContactId !== "none" ? Number(addContactId) : null,
      value: Number(fd.get("value") || 0),
      probability: Number(fd.get("probability") || 0),
      owner: fd.get("owner") as string || "",
      notes: fd.get("notes") as string || "",
    })
    setShowAddModal(null)
    setAddContactId("none")
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
  }

  const allLeads = Object.values(pipeline).flat()
  const totalLeads = allLeads.length
  const totalValue = allLeads
    .filter((l) => l.stage !== "Lost")
    .reduce((s, l) => s + (l.value || 0), 0)
  const won = pipeline["Won"]?.length || 0
  const closed = won + (pipeline["Lost"]?.length || 0)
  const convRate = closed > 0 ? Math.round((won / closed) * 100) : 0

  return (
    <AppLayout activePage="crm">
      <div className="px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold">CRM Pipeline</h1>
            <p className="text-sm text-muted-foreground">
              {totalLeads} leads &middot; Kanban board
            </p>
          </div>
          <Button variant="outline" size="sm" onClick={loadData} disabled={loading}>
            <RefreshCw className="h-4 w-4 mr-1" /> Refresh
          </Button>
        </div>

        {/* Stats bar */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
          <Card>
            <CardContent className="p-4 flex items-center gap-3">
              <div className="h-9 w-9 rounded-lg flex items-center justify-center bg-violet-100">
                <DollarSign className="h-4 w-4 text-[#6D28D9]" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Pipeline Value</p>
                <p className="text-lg font-bold">
                  {currency}{totalValue.toLocaleString("en-US", { minimumFractionDigits: 0 })}
                </p>
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
                <Badge variant="secondary" className="text-xs">{totalLeads}</Badge>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Total Leads</p>
                <p className="text-lg font-bold">{totalLeads}</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-destructive/10 border border-destructive/20 text-destructive rounded-lg text-sm">
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
        ) : (
          /* Kanban Board */
          <div className="flex gap-4 overflow-x-auto pb-4">
            {STAGES.map((stage) => {
              const leads = pipeline[stage] || []
              const { color, bg } = STAGE_CONFIG[stage]
              return (
                <div key={stage} className="flex-shrink-0 w-56">
                  {/* Column header */}
                  <div
                    className="rounded-t-xl px-3 py-2 flex items-center justify-between"
                    style={{ backgroundColor: color }}
                  >
                    <span className="text-white font-semibold text-sm">
                      {stage}{" "}
                      <span className="opacity-75 font-normal">({leads.length})</span>
                    </span>
                    <button
                      onClick={() => setShowAddModal(stage)}
                      className="text-white hover:opacity-75 transition-opacity p-0.5"
                      title={`Add lead to ${stage}`}
                    >
                      <Plus className="h-4 w-4" />
                    </button>
                  </div>

                  {/* Lead cards */}
                  <div
                    className="rounded-b-xl min-h-24 p-2 space-y-2"
                    style={{ backgroundColor: bg }}
                  >
                    {leads.length === 0 && (
                      <p className="text-xs text-center py-3" style={{ color: color + "99" }}>
                        No leads
                      </p>
                    )}
                    {leads.map((lead) => (
                      <div
                        key={lead.id}
                        className="bg-white rounded-lg shadow-sm p-3 cursor-pointer hover:shadow-md transition-shadow border-l-4"
                        style={{ borderColor: color }}
                        onClick={() => setSelectedLead(lead)}
                      >
                        <p className="text-sm font-semibold leading-tight mb-1">
                          {lead.title}
                        </p>
                        {lead.contact_name && (
                          <p className="text-xs text-muted-foreground mb-1">
                            {lead.contact_name}
                          </p>
                        )}
                        <Badge variant={stageBadgeVariant(stage)} className="text-xs mb-1">
                          {currency}{(lead.value || 0).toLocaleString("en-US", { minimumFractionDigits: 0 })}
                        </Badge>
                        {lead.owner && (
                          <p className="text-xs text-muted-foreground">
                            {lead.owner}
                          </p>
                        )}
                        {stage !== "Lost" && stage !== "Won" && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              moveLead(lead)
                            }}
                            className="mt-1.5 text-xs px-2 py-0.5 border border-border rounded hover:bg-muted transition-colors"
                          >
                            Move
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Lead Detail Modal */}
      <Dialog open={!!selectedLead} onOpenChange={(open) => !open && setSelectedLead(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Lead Detail</DialogTitle>
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
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {STAGES.map((s) => (
                      <SelectItem key={s} value={s}>{s}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label htmlFor="edit-value">Value ($)</Label>
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
                  className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                />
              </div>
              <DialogFooter className="gap-2 pt-2">
                <Button
                  type="button"
                  variant="destructive"
                  size="sm"
                  onClick={() => handleDeleteLead(selectedLead.id)}
                >
                  Delete
                </Button>
                <DialogClose asChild>
                  <Button type="button" variant="outline" size="sm">
                    Close
                  </Button>
                </DialogClose>
                <Button type="submit" size="sm">Save</Button>
              </DialogFooter>
            </form>
          )}
        </DialogContent>
      </Dialog>

      {/* Add Lead Modal */}
      <Dialog
        open={!!showAddModal}
        onOpenChange={(open) => {
          if (!open) { setShowAddModal(null); setAddContactId("none") }
        }}
      >
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Add Lead — {showAddModal}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleAddLead} className="space-y-3">
            <div className="space-y-1.5">
              <Label htmlFor="add-title">Title *</Label>
              <Input id="add-title" name="title" required />
            </div>
            <div className="space-y-1.5">
              <Label>Contact</Label>
              <Select value={addContactId} onValueChange={setAddContactId}>
                <SelectTrigger>
                  <SelectValue placeholder="(none)" />
                </SelectTrigger>
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
                <Label htmlFor="add-value">Value ($)</Label>
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
              <DialogClose asChild>
                <Button type="button" variant="outline">Cancel</Button>
              </DialogClose>
              <Button type="submit">Add Lead</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </AppLayout>
  )
}
