"use client"

import { useEffect, useState, useCallback } from "react"
import AppLayout from "@/components/layout/AppLayout"
import { toast } from "@/components/ui/toast"
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  fetchEmployees,
  fetchGoals,
  fetchAppraisals,
  updateAppraisal,
  fetchLeaveRequests,
  createLeaveRequest,
  fetchEmployeeSkills,
} from "@/lib/db"
import type { Goal, Appraisal, LeaveRequest, EmployeeSkill } from "@/lib/db"
import {
  Target,
  Star,
  CalendarDays,
  Zap,
  UserCheck,
  ChevronDown,
} from "lucide-react"

type Tab = "goals" | "appraisals" | "leave" | "skills"

interface Employee {
  id: number
  name: string
  designation?: string
  team?: string
}

function Spinner() {
  return (
    <div className="flex items-center justify-center py-20">
      <div
        className="h-8 w-8 rounded-full border-4 border-t-transparent animate-spin"
        style={{ borderColor: "#6D28D9", borderTopColor: "transparent" }}
      />
    </div>
  )
}

function statusColor(status: string) {
  const map: Record<string, string> = {
    Draft: "secondary",
    "In Progress": "default",
    Completed: "secondary",
    Pending: "secondary",
    Approved: "default",
    Rejected: "destructive",
    Delivered: "secondary",
    Ordered: "default",
  }
  return (map[status] ?? "secondary") as "default" | "secondary" | "destructive" | "outline"
}

// ---- My Goals Tab ----
function MyGoalsTab({ goals }: { goals: Goal[] }) {
  if (!goals.length) {
    return (
      <div className="text-center py-16 text-muted-foreground">
        No goals assigned to you yet.
      </div>
    )
  }
  return (
    <div className="space-y-3">
      {goals.map((g) => (
        <Card key={g.id} className="shadow-sm">
          <CardContent className="pt-4 pb-4">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm">{g.title}</p>
                {g.description && (
                  <p className="text-xs text-muted-foreground mt-0.5">{g.description}</p>
                )}
                {g.due_date && (
                  <p className="text-xs text-muted-foreground mt-1">Due: {g.due_date}</p>
                )}
              </div>
              <Badge variant={statusColor(g.status)} className="shrink-0">
                {g.status}
              </Badge>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

// ---- My Appraisals Tab ----
function MyAppraisalsTab({
  appraisals,
  onRefresh,
}: {
  appraisals: Appraisal[]
  onRefresh: () => void
}) {
  const [editing, setEditing] = useState<number | null>(null)
  const [selfRating, setSelfRating] = useState("")
  const [selfComments, setSelfComments] = useState("")
  const [saving, setSaving] = useState(false)

  function startEdit(a: Appraisal) {
    setEditing(a.id)
    setSelfRating(String(a.self_rating ?? ""))
    setSelfComments(a.self_comments ?? "")
  }

  async function handleSave(id: number) {
    const rating = parseFloat(selfRating)
    if (isNaN(rating) || rating < 0 || rating > 5) {
      toast("Rating must be 0–5", "error")
      return
    }
    setSaving(true)
    try {
      await updateAppraisal(id, {
        self_rating: rating,
        self_comments: selfComments,
        status: "In Progress",
      })
      toast("Self-assessment submitted", "success")
      setEditing(null)
      onRefresh()
    } catch {
      toast("Failed to save", "error")
    } finally {
      setSaving(false)
    }
  }

  if (!appraisals.length) {
    return (
      <div className="text-center py-16 text-muted-foreground">
        No appraisals found for you.
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {appraisals.map((a) => (
        <Card key={a.id} className="shadow-sm">
          <CardContent className="pt-4 pb-4 space-y-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-medium text-sm">{a.period}</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Manager rating: {a.manager_rating ?? "—"}
                </p>
                {a.manager_comments && (
                  <p className="text-xs text-muted-foreground mt-0.5 italic">
                    &ldquo;{a.manager_comments}&rdquo;
                  </p>
                )}
              </div>
              <Badge variant={statusColor(a.status)}>{a.status}</Badge>
            </div>

            {editing === a.id ? (
              <div className="space-y-2 pt-1">
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className="text-xs">Self Rating (0–5)</Label>
                    <Input
                      type="number"
                      min={0}
                      max={5}
                      step={0.5}
                      value={selfRating}
                      onChange={(e) => setSelfRating(e.target.value)}
                      className="h-8 text-sm"
                    />
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Comments</Label>
                  <textarea
                    value={selfComments}
                    onChange={(e) => setSelfComments(e.target.value)}
                    rows={3}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    placeholder="Describe your achievements this period..."
                  />
                </div>
                <div className="flex gap-2 pt-1">
                  <Button size="sm" disabled={saving} onClick={() => handleSave(a.id)}>
                    {saving ? "Saving…" : "Submit"}
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => setEditing(null)}>
                    Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">
                  Your rating: <span className="font-medium text-foreground">{a.self_rating ?? "—"}</span>
                </p>
                {a.self_comments && (
                  <p className="text-xs text-muted-foreground italic">&ldquo;{a.self_comments}&rdquo;</p>
                )}
                {(a.status === "Pending" || a.status === "In Progress") && (
                  <Button
                    size="sm"
                    variant="outline"
                    className="mt-2"
                    onClick={() => startEdit(a)}
                  >
                    Edit Self-Assessment
                  </Button>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

// ---- My Leave Tab ----
function MyLeaveTab({
  employeeId,
  leaves,
  onRefresh,
}: {
  employeeId: number
  leaves: LeaveRequest[]
  onRefresh: () => void
}) {
  const [showForm, setShowForm] = useState(false)
  const [leaveType, setLeaveType] = useState("Annual")
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [reason, setReason] = useState("")
  const [saving, setSaving] = useState(false)

  async function handleSubmit() {
    if (!startDate || !endDate) {
      toast("Start and end dates are required", "error")
      return
    }
    if (endDate < startDate) {
      toast("End date must be after start date", "error")
      return
    }
    setSaving(true)
    try {
      await createLeaveRequest({ employee_id: employeeId, leave_type: leaveType, start_date: startDate, end_date: endDate, reason })
      toast("Leave request submitted", "success")
      setShowForm(false)
      setStartDate("")
      setEndDate("")
      setReason("")
      setLeaveType("Annual")
      onRefresh()
    } catch {
      toast("Failed to submit", "error")
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Submit form */}
      <Card className="shadow-sm">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-semibold">Request Leave</CardTitle>
            <Button
              size="sm"
              variant="outline"
              onClick={() => setShowForm(!showForm)}
              className="h-7 text-xs gap-1"
            >
              {showForm ? "Cancel" : "New Request"}
              {!showForm && <ChevronDown className="h-3 w-3" />}
            </Button>
          </div>
        </CardHeader>
        {showForm && (
          <CardContent className="space-y-3 pt-0">
            <div className="space-y-1">
              <Label className="text-xs">Leave Type</Label>
              <Select value={leaveType} onValueChange={setLeaveType}>
                <SelectTrigger className="h-8 text-sm">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {["Annual", "Sick", "Unpaid", "Other"].map((t) => (
                    <SelectItem key={t} value={t}>{t}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label className="text-xs">Start Date</Label>
                <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="h-8 text-sm" />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">End Date</Label>
                <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="h-8 text-sm" />
              </div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Reason (optional)</Label>
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                rows={2}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                placeholder="Brief reason for leave..."
              />
            </div>
            <Button size="sm" disabled={saving} onClick={handleSubmit}>
              {saving ? "Submitting…" : "Submit Request"}
            </Button>
          </CardContent>
        )}
      </Card>

      {/* Leave history */}
      <div>
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">
          My Leave Requests
        </p>
        {!leaves.length ? (
          <div className="text-center py-10 text-muted-foreground text-sm">No leave requests yet.</div>
        ) : (
          <div className="space-y-2">
            {leaves.map((l) => (
              <Card key={l.id} className="shadow-sm">
                <CardContent className="pt-3 pb-3">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="text-sm font-medium">{l.leave_type} Leave</p>
                      <p className="text-xs text-muted-foreground">
                        {l.start_date} → {l.end_date}
                      </p>
                      {l.reason && (
                        <p className="text-xs text-muted-foreground mt-0.5">{l.reason}</p>
                      )}
                      {l.reviewed_by && (
                        <p className="text-xs text-muted-foreground mt-0.5">
                          Reviewed by: {l.reviewed_by}
                        </p>
                      )}
                    </div>
                    <Badge variant={statusColor(l.status)}>{l.status}</Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// ---- My Skills Tab ----
function MySkillsTab({ skills }: { skills: EmployeeSkill[] }) {
  if (!skills.length) {
    return (
      <div className="text-center py-16 text-muted-foreground">
        No skills on your profile yet. Ask your manager to add them.
      </div>
    )
  }

  const grouped = skills.reduce<Record<string, EmployeeSkill[]>>((acc, s) => {
    const cat = s.skill_category ?? "Other"
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(s)
    return acc
  }, {})

  const proficiencyColor: Record<string, string> = {
    Beginner: "bg-blue-100 text-blue-700",
    Intermediate: "bg-yellow-100 text-yellow-700",
    Advanced: "bg-green-100 text-green-700",
    Expert: "bg-purple-100 text-purple-700",
  }

  return (
    <div className="space-y-4">
      {Object.entries(grouped).map(([cat, items]) => (
        <Card key={cat} className="shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold">{cat}</CardTitle>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="flex flex-wrap gap-2">
              {items.map((s) => (
                <span
                  key={s.id}
                  className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${proficiencyColor[s.proficiency] ?? "bg-gray-100 text-gray-700"}`}
                >
                  {s.skill_name}
                  <span className="opacity-60">· {s.proficiency}</span>
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

// ---- Main Page ----
export default function EmployeePortalPage() {
  const [tab, setTab] = useState<Tab>("goals")
  const [employees, setEmployees] = useState<Employee[]>([])
  const [selectedId, setSelectedId] = useState<string>("")

  const [goals, setGoals] = useState<Goal[]>([])
  const [appraisals, setAppraisals] = useState<Appraisal[]>([])
  const [leaves, setLeaves] = useState<LeaveRequest[]>([])
  const [skills, setSkills] = useState<EmployeeSkill[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchEmployees().then((rows) => setEmployees(rows as Employee[])).catch(() => {})
  }, [])

  const loadData = useCallback(async (empId: number) => {
    setLoading(true)
    try {
      const [g, a, l, s] = await Promise.all([
        fetchGoals(),
        fetchAppraisals(),
        fetchLeaveRequests(),
        fetchEmployeeSkills(empId),
      ])
      setGoals(g.filter((x) => x.employee_id === empId))
      setAppraisals(a.filter((x) => x.employee_id === empId))
      setLeaves(l.filter((x) => x.employee_id === empId))
      setSkills(s)
    } catch {
      toast("Failed to load data", "error")
    } finally {
      setLoading(false)
    }
  }, [])

  function handleSelectEmployee(id: string) {
    setSelectedId(id)
    loadData(Number(id))
  }

  function refreshData() {
    if (selectedId) loadData(Number(selectedId))
  }

  const selectedEmployee = employees.find((e) => String(e.id) === selectedId)

  const tabs: { key: Tab; label: string; icon: React.ReactNode; count?: number }[] = [
    { key: "goals", label: "My Goals", icon: <Target className="h-4 w-4" />, count: goals.length || undefined },
    { key: "appraisals", label: "My Appraisals", icon: <Star className="h-4 w-4" />, count: appraisals.length || undefined },
    { key: "leave", label: "My Leave", icon: <CalendarDays className="h-4 w-4" />, count: leaves.length || undefined },
    { key: "skills", label: "My Skills", icon: <Zap className="h-4 w-4" />, count: skills.length || undefined },
  ]

  return (
    <AppLayout activePage="employee-portal">
      <div className="p-4 md:p-6 max-w-3xl mx-auto space-y-5">
        {/* Header */}
        <div className="flex items-center gap-3">
          <div
            className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
            style={{ backgroundColor: "#6D28D9" }}
          >
            <UserCheck className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold">Employee Self-Service</h1>
            <p className="text-xs text-muted-foreground">View your goals, appraisals, leave &amp; skills</p>
          </div>
        </div>

        {/* Employee picker */}
        <Card className="shadow-sm">
          <CardContent className="pt-4 pb-4">
            <div className="space-y-1.5">
              <Label className="text-sm font-medium">Who are you?</Label>
              <Select value={selectedId} onValueChange={handleSelectEmployee}>
                <SelectTrigger className="w-full max-w-xs">
                  <SelectValue placeholder="Select your name…" />
                </SelectTrigger>
                <SelectContent>
                  {employees.map((e) => (
                    <SelectItem key={e.id} value={String(e.id)}>
                      {e.name}{e.designation ? ` — ${e.designation}` : ""}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground">
                Login will be added in a future update. For now, select your name above.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Content — only show after an employee is selected */}
        {selectedId && (
          <>
            {/* Welcome banner */}
            <div className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-violet-50 border border-violet-100">
              <div className="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold shrink-0" style={{ backgroundColor: "#6D28D9" }}>
                {(selectedEmployee?.name ?? "?").slice(0, 1).toUpperCase()}
              </div>
              <div>
                <p className="text-sm font-medium text-[#6D28D9]">
                  Hi, {selectedEmployee?.name?.split(" ")[0]}!
                </p>
                {selectedEmployee?.designation && (
                  <p className="text-xs text-violet-600/70">{selectedEmployee.designation}</p>
                )}
              </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-1 border-b border-border overflow-x-auto">
              {tabs.map((t) => (
                <button
                  key={t.key}
                  onClick={() => setTab(t.key)}
                  className={`flex items-center gap-1.5 px-3 py-2.5 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                    tab === t.key
                      ? "border-[#6D28D9] text-[#6D28D9]"
                      : "border-transparent text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {t.icon}
                  {t.label}
                  {t.count !== undefined && (
                    <span className={`text-xs px-1.5 py-0.5 rounded-full ${tab === t.key ? "bg-violet-100 text-[#6D28D9]" : "bg-muted text-muted-foreground"}`}>
                      {t.count}
                    </span>
                  )}
                </button>
              ))}
            </div>

            {/* Tab content */}
            {loading ? (
              <Spinner />
            ) : (
              <>
                {tab === "goals" && <MyGoalsTab goals={goals} />}
                {tab === "appraisals" && (
                  <MyAppraisalsTab appraisals={appraisals} onRefresh={refreshData} />
                )}
                {tab === "leave" && (
                  <MyLeaveTab employeeId={Number(selectedId)} leaves={leaves} onRefresh={refreshData} />
                )}
                {tab === "skills" && <MySkillsTab skills={skills} />}
              </>
            )}
          </>
        )}
      </div>
    </AppLayout>
  )
}
