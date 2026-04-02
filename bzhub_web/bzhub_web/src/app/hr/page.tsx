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
import {
  fetchEmployees,
  createEmployee,
  updateEmployee,
  deleteEmployee,
  fetchPayrolls,
  createPayroll,
  fetchGoals,
  createGoal,
  updateGoal,
  deleteGoal,
  createGoalCheckin,
  fetchAppraisals,
  createAppraisal,
  updateAppraisal,
  deleteAppraisal,
  fetchSkills,
  createSkill,
  fetchEmployeeSkills,
  addEmployeeSkill,
  deleteEmployeeSkill,
  fetchLeaveRequests,
  createLeaveRequest,
  updateLeaveRequestStatus,
  deleteLeaveRequest,
  fetchLeaveBalance,
  applyLeaveToBalance,
  processYearEndLeave,
  fetchLeaveDeductionsByPeriod,
  countDays,
  LEAVE_RATE,
  SICK_QUOTA,
  PERSONAL_QUOTA,
  PERSONAL_CARRY_CAP,
} from "@/lib/db"
import type { Goal, Appraisal, Skill, EmployeeSkill, LeaveRequest, LeaveBalance } from "@/lib/db"
import { Plus, Users, DollarSign, Target, Star, Zap, CalendarDays, Check, X, Download } from "lucide-react"
import { downloadCSV } from "@/lib/export"
import { Separator } from "@/components/ui/separator"
import CustomFieldRenderer from "@/components/CustomFieldRenderer"
import { getEntityFields } from "@/lib/customFields"
import { fetchCustomData, upsertCustomData } from "@/lib/db"

type Tab = "employees" | "payroll" | "goals" | "appraisals" | "skills" | "leave"

interface Employee {
  id: number
  emp_number?: string
  name: string
  designation?: string
  team?: string
  email?: string
  phone?: string
  is_active?: number | boolean
}

interface PayrollRecord {
  id: number
  employee_id: number
  employee_name?: string
  period_start?: string
  period_end?: string
  gross_pay?: number
  net_pay?: number
  status?: string
}

// ---- Spinner ----
function Spinner() {
  return (
    <div className="flex items-center justify-center py-20">
      <div
        className="h-8 w-8 rounded-full border-4 border-t-transparent animate-spin"
        style={{ borderColor: "var(--brand-color)", borderTopColor: "transparent" }}
      />
    </div>
  )
}

// ---- Error Box ----
function ErrorBox({ msg }: { msg: string }) {
  return (
    <div className="p-3 bg-destructive/10 border border-destructive/20 text-destructive rounded-lg text-sm">
      {msg}
    </div>
  )
}

// ---- Employees Tab ----
function EmployeesTab() {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [showAdd, setShowAdd] = useState(false)
  const [editing, setEditing] = useState<Employee | null>(null)
  const customFields = getEntityFields('employee')

  const load = useCallback(async () => {
    try {
      setError("")
      const data = await fetchEmployees()
      const list = Array.isArray(data) ? data : []
      setEmployees(list)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load employees")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  async function handleDelete(id: number, name: string) {
    if (!confirm(`Delete employee "${name}"?`)) return
    try {
      await deleteEmployee(id)
      await load()
      toast("Employee deleted", "success")
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : "Delete failed", "error")
    }
  }

  async function handleSave(
    e: React.FormEvent<HTMLFormElement>,
    employeeId: number | undefined,
    customValues: Record<string, unknown>
  ) {
    e.preventDefault()
    const fd = new FormData(e.currentTarget)
    const data = {
      name: fd.get("name") as string,
      designation: fd.get("designation") as string,
      team: fd.get("team") as string,
      email: fd.get("email") as string,
      phone: fd.get("phone") as string,
    }
    try {
      let savedId = employeeId
      if (employeeId) {
        await updateEmployee(employeeId, data)
        setEditing(null)
        toast("Employee updated", "success")
      } else {
        savedId = await createEmployee(data)
        setShowAdd(false)
        toast("Employee added", "success")
      }
      if (customFields.length > 0 && savedId) {
        await upsertCustomData('employee', String(savedId), customValues)
      }
      await load()
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : "Save failed", "error")
    }
  }

  function isActive(emp: Employee): boolean {
    if (emp.is_active === undefined || emp.is_active === null) return true
    if (typeof emp.is_active === "boolean") return emp.is_active
    return emp.is_active !== 0
  }

  function EmployeeForm({ emp, onClose }: { emp?: Employee; onClose: () => void }) {
    const [customValues, setCustomValues] = useState<Record<string, unknown>>({})

    useEffect(() => {
      if (emp) {
        fetchCustomData('employee', String(emp.id)).then(setCustomValues)
      }
    }, [emp])

    return (
      <form onSubmit={(e) => handleSave(e, emp?.id, customValues)}>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 py-4">
          <div className="col-span-2 space-y-1.5">
            <Label htmlFor="name">Full Name *</Label>
            <Input name="name" required defaultValue={emp?.name} placeholder="e.g. Jane Smith" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="designation">Designation</Label>
            <Input name="designation" defaultValue={emp?.designation} placeholder="e.g. Engineer" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="team">Department</Label>
            <Input name="team" defaultValue={emp?.team} placeholder="e.g. Engineering" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="email">Email</Label>
            <Input name="email" type="email" defaultValue={emp?.email} placeholder="jane@company.com" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="phone">Phone</Label>
            <Input name="phone" defaultValue={emp?.phone} placeholder="+1 555 000 0000" />
          </div>
          {customFields.length > 0 && (
            <div className="col-span-2 space-y-3">
              <Separator />
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                Custom Fields
              </p>
              <CustomFieldRenderer
                fields={customFields}
                values={customValues}
                onChange={(id, val) => setCustomValues(prev => ({ ...prev, [id]: val }))}
              />
            </div>
          )}
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
          </DialogClose>
          <Button type="submit">{emp ? "Save Changes" : "Add Employee"}</Button>
        </DialogFooter>
      </form>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">{employees.length} employees</p>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => downloadCSV("employees.csv", employees.map(e => ({
              id: e.id,
              emp_number: e.emp_number ?? "",
              name: e.name,
              designation: e.designation ?? "",
              team: e.team ?? "",
              email: e.email ?? "",
              phone: e.phone ?? "",
              is_active: e.is_active ? "Yes" : "No",
            })))}
          >
            <Download className="h-4 w-4 mr-1" /> Export CSV
          </Button>
          <Button onClick={() => setShowAdd(true)} size="sm">
            <Plus className="h-4 w-4 mr-1" /> Add Employee
          </Button>
        </div>
      </div>

      {error && <ErrorBox msg={error} />}

      {/* Add dialog */}
      <Dialog open={showAdd} onOpenChange={setShowAdd}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Employee</DialogTitle>
          </DialogHeader>
          <EmployeeForm onClose={() => setShowAdd(false)} />
        </DialogContent>
      </Dialog>

      {/* Edit dialog */}
      <Dialog open={!!editing} onOpenChange={(open) => !open && setEditing(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit — {editing?.name}</DialogTitle>
          </DialogHeader>
          {editing && <EmployeeForm emp={editing} onClose={() => setEditing(null)} />}
        </DialogContent>
      </Dialog>

      {loading ? (
        <Spinner />
      ) : (
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Dept / Role</TableHead>
                <TableHead>Phone / Email</TableHead>
                <TableHead>Status</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {employees.map((emp) => (
                <TableRow key={emp.id}>
                  <TableCell className="font-medium">{emp.name}</TableCell>
                  <TableCell className="text-muted-foreground text-xs">
                    <span className="font-medium text-foreground">{emp.team || "—"}</span>
                    {emp.designation && (
                      <span className="block">{emp.designation}</span>
                    )}
                  </TableCell>
                  <TableCell className="text-xs">
                    {emp.phone && <span className="block">{emp.phone}</span>}
                    {emp.email && (
                      <span className="block text-muted-foreground">{emp.email}</span>
                    )}
                    {!emp.phone && !emp.email && <span className="text-muted-foreground">—</span>}
                  </TableCell>
                  <TableCell>
                    <Badge variant={isActive(emp) ? "secondary" : "outline"}>
                      {isActive(emp) ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 text-xs text-[var(--brand-color)]"
                        onClick={() => setEditing(emp)}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 text-xs text-destructive"
                        onClick={() => handleDelete(emp.id, emp.name)}
                      >
                        Delete
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
              {employees.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-muted-foreground italic py-8">
                    No employees found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  )
}

// ---- Payroll Tab ----
function PayrollTab() {
  const [records, setRecords] = useState<PayrollRecord[]>([])
  const [employees, setEmployees] = useState<Employee[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [showAdd, setShowAdd] = useState(false)
  const [addEmployeeId, setAddEmployeeId] = useState("")
  const [addStatus, setAddStatus] = useState("Draft")
  const [addPeriod, setAddPeriod] = useState("")        // e.g. "2026-04"
  const [lopDeductions, setLopDeductions] = useState(0) // auto-loaded from leave_deductions

  const load = useCallback(async () => {
    try {
      setError("")
      const [payrollData, empData] = await Promise.all([fetchPayrolls(), fetchEmployees()])
      setRecords(Array.isArray(payrollData) ? payrollData : [])
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const empResult = empData as any
      setEmployees(Array.isArray(empResult) ? empResult : (empResult?.employees ?? []))
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load payroll")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  // Auto-load LOP deductions when employee + period are both set
  useEffect(() => {
    setLopDeductions(0)
    if (!addEmployeeId || !addPeriod.match(/^\d{4}-\d{2}$/)) return
    fetchLeaveDeductionsByPeriod(addPeriod).then((deductions) => {
      const empDeductions = deductions.filter(d => d.employee_id === Number(addEmployeeId))
      const total = empDeductions.reduce((sum, d) => sum + Number(d.amount), 0)
      setLopDeductions(total)
    }).catch(() => null)
  }, [addEmployeeId, addPeriod])

  async function handleAdd(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const fd = new FormData(e.currentTarget)
    const manualDeductions = Number(fd.get("deductions") || 0)
    try {
      await createPayroll({
        employee_id: Number(addEmployeeId),
        period_start: fd.get("period_start") as string,
        period_end: fd.get("period_end") as string,
        basic: Number(fd.get("basic")),
        allowances: Number(fd.get("allowances") || 0),
        deductions: manualDeductions + lopDeductions,
        status: addStatus,
      })
      setShowAdd(false)
      setAddEmployeeId("")
      setAddStatus("Draft")
      setAddPeriod("")
      setLopDeductions(0)
      await load()
      toast("Payroll record created", "success")
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : "Failed to create payroll", "error")
    }
  }

  const now = new Date()
  const thisMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`
  const monthRecords = records.filter((r) => (r.period_start ?? "").startsWith(thisMonth))
  const monthTotal = monthRecords.reduce((sum, r) => sum + Number(r.gross_pay || 0), 0)

  function payrollStatusVariant(status?: string): "default" | "secondary" | "destructive" | "outline" {
    if (!status) return "secondary"
    const s = status.toLowerCase()
    if (s === "paid") return "default"
    if (s === "draft") return "outline"
    return "secondary"
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardContent className="p-4 flex items-center gap-4">
          <div
            className="h-10 w-10 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{ backgroundColor: "color-mix(in srgb, var(--brand-color) 12%, transparent)" }}
          >
            <DollarSign className="h-5 w-5" style={{ color: "var(--brand-color)" }} />
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Total Payroll This Month</p>
            <p className="text-xl font-bold">${Number(monthTotal || 0).toFixed(2)}</p>
            <p className="text-xs text-muted-foreground">{monthRecords.length} records</p>
          </div>
        </CardContent>
      </Card>

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">{records.length} records</p>
        <Button onClick={() => setShowAdd(true)} size="sm">+ Create Payroll</Button>
      </div>

      {error && <ErrorBox msg={error} />}

      {loading ? (
        <Spinner />
      ) : (
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Employee</TableHead>
                <TableHead>Period</TableHead>
                <TableHead className="text-right">Gross Pay</TableHead>
                <TableHead className="text-right">Net Pay</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {records.map((r) => (
                <TableRow key={r.id}>
                  <TableCell className="font-medium">
                    {r.employee_name ?? `Employee #${r.employee_id}`}
                  </TableCell>
                  <TableCell className="text-muted-foreground text-xs">
                    {r.period_start ?? "—"}
                  </TableCell>
                  <TableCell className="text-right">${Number(r.gross_pay || 0).toFixed(2)}</TableCell>
                  <TableCell className="text-right font-medium">${Number(r.net_pay || 0).toFixed(2)}</TableCell>
                  <TableCell>
                    <Badge variant={payrollStatusVariant(r.status)}>{r.status ?? "Draft"}</Badge>
                  </TableCell>
                </TableRow>
              ))}
              {records.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-muted-foreground italic py-8">
                    No payroll records found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Create Payroll Modal */}
      <Dialog open={showAdd} onOpenChange={(open) => {
        setShowAdd(open)
        if (!open) { setAddEmployeeId(""); setAddStatus("Draft"); setAddPeriod(""); setLopDeductions(0) }
      }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Payroll</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleAdd} className="space-y-4">
            <div className="space-y-1">
              <label className="text-sm font-medium">Employee</label>
              <Select value={addEmployeeId} onValueChange={setAddEmployeeId} required>
                <SelectTrigger><SelectValue placeholder="Select employee" /></SelectTrigger>
                <SelectContent>
                  {employees.map((emp) => (
                    <SelectItem key={emp.id} value={String(emp.id)}>{emp.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-sm font-medium">Period Start</label>
                <Input name="period_start" type="text" placeholder="2026-04-01" required
                  onChange={(e) => setAddPeriod(e.target.value.slice(0, 7))} />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium">Period End</label>
                <Input name="period_end" type="text" placeholder="2026-04-30" required />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <div className="space-y-1">
                <label className="text-sm font-medium">Basic</label>
                <Input name="basic" type="number" min="0" step="0.01" placeholder="0.00" required />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium">Allowances</label>
                <Input name="allowances" type="number" min="0" step="0.01" placeholder="0.00" />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-medium">Other Deductions</label>
                <Input name="deductions" type="number" min="0" step="0.01" placeholder="0.00" />
              </div>
            </div>
            {lopDeductions > 0 && (
              <div className="rounded-md bg-orange-50 border border-orange-200 p-3 text-sm text-orange-700">
                ₹{lopDeductions} loss-of-pay deduction auto-added from approved leave this period.
              </div>
            )}
            <div className="space-y-1">
              <label className="text-sm font-medium">Status</label>
              <Select value={addStatus} onValueChange={setAddStatus}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="Draft">Draft</SelectItem>
                  <SelectItem value="Paid">Paid</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <DialogFooter>
              <DialogClose asChild>
                <Button type="button" variant="outline">Cancel</Button>
              </DialogClose>
              <Button type="submit">Create</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}

// ---- Goals Tab ----
function GoalsTab() {
  const [goals, setGoals] = useState<Goal[]>([])
  const [employees, setEmployees] = useState<Employee[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [showAdd, setShowAdd] = useState(false)
  const [editing, setEditing] = useState<Goal | null>(null)
  const [checkinGoal, setCheckinGoal] = useState<Goal | null>(null)

  // Add form state
  const [addEmployeeId, setAddEmployeeId] = useState("")
  const [addStatus, setAddStatus] = useState("Draft")

  // Edit form state
  const [editStatus, setEditStatus] = useState("Draft")

  // Checkin state
  const [checkinProgress, setCheckinProgress] = useState(0)
  const [checkinNotes, setCheckinNotes] = useState("")

  const load = useCallback(async () => {
    try {
      setError("")
      const [goalsData, empData] = await Promise.all([fetchGoals(), fetchEmployees()])
      setGoals(Array.isArray(goalsData) ? goalsData : [])
      setEmployees(Array.isArray(empData) ? empData : [])
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load goals")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  async function handleAdd(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const fd = new FormData(e.currentTarget)
    try {
      await createGoal({
        employee_id: Number(addEmployeeId),
        title: fd.get("title") as string,
        description: fd.get("description") as string,
        due_date: fd.get("due_date") as string,
        status: addStatus,
      })
      setShowAdd(false)
      setAddEmployeeId("")
      setAddStatus("Draft")
      await load()
      toast("Goal created", "success")
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : "Failed to create goal", "error")
    }
  }

  async function handleEdit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (!editing) return
    const fd = new FormData(e.currentTarget)
    try {
      await updateGoal(editing.id, {
        title: fd.get("title") as string,
        description: fd.get("description") as string,
        due_date: fd.get("due_date") as string,
        status: editStatus,
      })
      setEditing(null)
      await load()
      toast("Goal updated", "success")
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : "Failed to update goal", "error")
    }
  }

  async function handleDelete(id: number, title: string) {
    if (!confirm(`Delete goal "${title}"?`)) return
    try {
      await deleteGoal(id)
      await load()
      toast("Goal deleted", "success")
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : "Delete failed", "error")
    }
  }

  async function handleCheckin(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (!checkinGoal) return
    try {
      await createGoalCheckin({
        goal_id: checkinGoal.id,
        progress_pct: checkinProgress,
        notes: checkinNotes,
        checked_by: "admin",
      })
      setCheckinGoal(null)
      setCheckinProgress(0)
      setCheckinNotes("")
      toast("Check-in logged", "success")
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : "Check-in failed", "error")
    }
  }

  function goalStatusVariant(status: string): "default" | "secondary" | "destructive" | "outline" {
    switch (status.toLowerCase()) {
      case "completed": return "default"
      case "active": return "secondary"
      case "cancelled": return "destructive"
      default: return "outline"
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">{goals.length} goals</p>
        <Button onClick={() => setShowAdd(true)} size="sm">
          <Plus className="h-4 w-4 mr-1" /> Add Goal
        </Button>
      </div>

      {error && <ErrorBox msg={error} />}

      {/* Add Goal Dialog */}
      <Dialog open={showAdd} onOpenChange={(open) => { setShowAdd(open); if (!open) { setAddEmployeeId(""); setAddStatus("Draft") } }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Goal</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleAdd}>
            <div className="space-y-4 py-4">
              <div className="space-y-1.5">
                <Label>Employee *</Label>
                <Select value={addEmployeeId} onValueChange={setAddEmployeeId} required>
                  <SelectTrigger>
                    <SelectValue placeholder="Select employee" />
                  </SelectTrigger>
                  <SelectContent>
                    {employees.map((emp) => (
                      <SelectItem key={emp.id} value={String(emp.id)}>{emp.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="title">Goal Title *</Label>
                <Input name="title" required placeholder="e.g. Complete onboarding training" />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="description">Description</Label>
                <Input name="description" placeholder="Optional details" />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="due_date">Due Date</Label>
                <Input name="due_date" type="date" />
              </div>
              <div className="space-y-1.5">
                <Label>Status</Label>
                <Select value={addStatus} onValueChange={setAddStatus}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {["Draft", "Active", "Completed", "Cancelled"].map((s) => (
                      <SelectItem key={s} value={s}>{s}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <DialogClose asChild>
                <Button type="button" variant="outline">Cancel</Button>
              </DialogClose>
              <Button type="submit" disabled={!addEmployeeId}>Add Goal</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Edit Goal Dialog */}
      <Dialog open={!!editing} onOpenChange={(open) => !open && setEditing(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Goal</DialogTitle>
          </DialogHeader>
          {editing && (
            <form onSubmit={handleEdit}>
              <div className="space-y-4 py-4">
                <div className="space-y-1.5">
                  <Label htmlFor="title">Goal Title *</Label>
                  <Input name="title" required defaultValue={editing.title} />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="description">Description</Label>
                  <Input name="description" defaultValue={editing.description} />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="due_date">Due Date</Label>
                  <Input name="due_date" type="date" defaultValue={editing.due_date} />
                </div>
                <div className="space-y-1.5">
                  <Label>Status</Label>
                  <Select value={editStatus} onValueChange={setEditStatus}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {["Draft", "Active", "Completed", "Cancelled"].map((s) => (
                        <SelectItem key={s} value={s}>{s}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter>
                <DialogClose asChild>
                  <Button type="button" variant="outline">Cancel</Button>
                </DialogClose>
                <Button type="submit">Save Changes</Button>
              </DialogFooter>
            </form>
          )}
        </DialogContent>
      </Dialog>

      {/* Check-in Dialog */}
      <Dialog open={!!checkinGoal} onOpenChange={(open) => { if (!open) { setCheckinGoal(null); setCheckinProgress(0); setCheckinNotes("") } }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Check-in — {checkinGoal?.title}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCheckin}>
            <div className="space-y-4 py-4">
              <div className="space-y-1.5">
                <Label>Progress ({checkinProgress}%)</Label>
                <input
                  type="range"
                  min={0}
                  max={100}
                  step={5}
                  value={checkinProgress}
                  onChange={(e) => setCheckinProgress(Number(e.target.value))}
                  className="w-full accent-[var(--brand-color)]"
                />
              </div>
              <div className="space-y-1.5">
                <Label>Notes</Label>
                <Input
                  value={checkinNotes}
                  onChange={(e) => setCheckinNotes(e.target.value)}
                  placeholder="What was accomplished?"
                />
              </div>
            </div>
            <DialogFooter>
              <DialogClose asChild>
                <Button type="button" variant="outline">Cancel</Button>
              </DialogClose>
              <Button type="submit">Log Check-in</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {loading ? (
        <Spinner />
      ) : (
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Employee</TableHead>
                <TableHead>Goal Title</TableHead>
                <TableHead>Due Date</TableHead>
                <TableHead>Status</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {goals.map((g) => (
                <TableRow key={g.id}>
                  <TableCell className="font-medium">{g.employee_name ?? `#${g.employee_id}`}</TableCell>
                  <TableCell>{g.title}</TableCell>
                  <TableCell className="text-muted-foreground text-xs">{g.due_date ?? "—"}</TableCell>
                  <TableCell>
                    <Badge variant={goalStatusVariant(g.status)}>{g.status}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 text-xs text-[var(--brand-color)]"
                        onClick={() => { setCheckinGoal(g); setCheckinProgress(0); setCheckinNotes("") }}
                      >
                        Check-in
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 text-xs text-[var(--brand-color)]"
                        onClick={() => { setEditing(g); setEditStatus(g.status) }}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 text-xs text-destructive"
                        onClick={() => handleDelete(g.id, g.title)}
                      >
                        Delete
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
              {goals.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} className="text-center text-muted-foreground italic py-8">
                    No goals found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  )
}

// ---- Appraisals Tab ----
function AppraisalsTab() {
  const [appraisals, setAppraisals] = useState<Appraisal[]>([])
  const [employees, setEmployees] = useState<Employee[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [showAdd, setShowAdd] = useState(false)
  const [editing, setEditing] = useState<Appraisal | null>(null)

  // Add form state
  const [addEmployeeId, setAddEmployeeId] = useState("")
  const [addStatus, setAddStatus] = useState("Pending")

  // Edit form state
  const [editStatus, setEditStatus] = useState("Pending")

  const load = useCallback(async () => {
    try {
      setError("")
      const [apprData, empData] = await Promise.all([fetchAppraisals(), fetchEmployees()])
      setAppraisals(Array.isArray(apprData) ? apprData : [])
      setEmployees(Array.isArray(empData) ? empData : [])
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load appraisals")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  async function handleAdd(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const fd = new FormData(e.currentTarget)
    try {
      await createAppraisal({
        employee_id: Number(addEmployeeId),
        period: fd.get("period") as string,
        self_rating: Number(fd.get("self_rating")),
        manager_rating: Number(fd.get("manager_rating")),
        self_comments: fd.get("self_comments") as string,
        manager_comments: fd.get("manager_comments") as string,
        status: addStatus,
      })
      setShowAdd(false)
      setAddEmployeeId("")
      setAddStatus("Pending")
      await load()
      toast("Appraisal created", "success")
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : "Failed to create appraisal", "error")
    }
  }

  async function handleEdit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (!editing) return
    const fd = new FormData(e.currentTarget)
    try {
      await updateAppraisal(editing.id, {
        period: fd.get("period") as string,
        self_rating: Number(fd.get("self_rating")),
        manager_rating: Number(fd.get("manager_rating")),
        self_comments: fd.get("self_comments") as string,
        manager_comments: fd.get("manager_comments") as string,
        status: editStatus,
      })
      setEditing(null)
      await load()
      toast("Appraisal updated", "success")
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : "Failed to update appraisal", "error")
    }
  }

  async function handleDelete(id: number) {
    if (!confirm("Delete this appraisal?")) return
    try {
      await deleteAppraisal(id)
      await load()
      toast("Appraisal deleted", "success")
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : "Delete failed", "error")
    }
  }

  function appraisalStatusVariant(status: string): "default" | "secondary" | "destructive" | "outline" {
    switch (status.toLowerCase()) {
      case "completed": return "default"
      case "in progress": return "secondary"
      default: return "outline"
    }
  }

  function overallScore(a: Appraisal): string {
    const s = a.self_rating
    const m = a.manager_rating
    if (!s && !m) return "—"
    if (!s) return m.toFixed(1)
    if (!m) return s.toFixed(1)
    return ((s + m) / 2).toFixed(1)
  }

  function AppraisalForm({ appr, onClose, statusValue, onStatusChange }: {
    appr?: Appraisal
    onClose: () => void
    statusValue: string
    onStatusChange: (v: string) => void
  }) {
    return (
      <form onSubmit={appr ? handleEdit : handleAdd}>
        <div className="space-y-4 py-4">
          {!appr && (
            <div className="space-y-1.5">
              <Label>Employee *</Label>
              <Select value={addEmployeeId} onValueChange={setAddEmployeeId} required>
                <SelectTrigger>
                  <SelectValue placeholder="Select employee" />
                </SelectTrigger>
                <SelectContent>
                  {employees.map((emp) => (
                    <SelectItem key={emp.id} value={String(emp.id)}>{emp.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
          <div className="space-y-1.5">
            <Label htmlFor="period">Period *</Label>
            <Input name="period" required defaultValue={appr?.period} placeholder="e.g. Q1 2026" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="self_rating">Self Rating (1–5)</Label>
              <Input name="self_rating" type="number" min={1} max={5} defaultValue={appr?.self_rating ?? 3} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="manager_rating">Manager Rating (1–5)</Label>
              <Input name="manager_rating" type="number" min={1} max={5} defaultValue={appr?.manager_rating ?? 3} />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="self_comments">Self Comments</Label>
            <Input name="self_comments" defaultValue={appr?.self_comments} placeholder="Employee self-assessment" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="manager_comments">Manager Comments</Label>
            <Input name="manager_comments" defaultValue={appr?.manager_comments} placeholder="Manager feedback" />
          </div>
          <div className="space-y-1.5">
            <Label>Status</Label>
            <Select value={statusValue} onValueChange={onStatusChange}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {["Pending", "In Progress", "Approved", "Rejected", "Completed"].map((s) => (
                  <SelectItem key={s} value={s}>{s}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
          </DialogClose>
          <Button type="submit" disabled={!appr && !addEmployeeId}>
            {appr ? "Save Changes" : "Create Appraisal"}
          </Button>
        </DialogFooter>
      </form>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">{appraisals.length} appraisals</p>
        <Button onClick={() => setShowAdd(true)} size="sm">
          <Plus className="h-4 w-4 mr-1" /> New Appraisal
        </Button>
      </div>

      {error && <ErrorBox msg={error} />}

      {/* Add Dialog */}
      <Dialog open={showAdd} onOpenChange={(open) => { setShowAdd(open); if (!open) { setAddEmployeeId(""); setAddStatus("Pending") } }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>New Appraisal</DialogTitle>
          </DialogHeader>
          <AppraisalForm onClose={() => setShowAdd(false)} statusValue={addStatus} onStatusChange={setAddStatus} />
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={!!editing} onOpenChange={(open) => !open && setEditing(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Appraisal — {editing?.employee_name}</DialogTitle>
          </DialogHeader>
          {editing && (
            <AppraisalForm
              appr={editing}
              onClose={() => setEditing(null)}
              statusValue={editStatus}
              onStatusChange={setEditStatus}
            />
          )}
        </DialogContent>
      </Dialog>

      {loading ? (
        <Spinner />
      ) : (
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Employee</TableHead>
                <TableHead>Period</TableHead>
                <TableHead>Self Rating</TableHead>
                <TableHead>Manager Rating</TableHead>
                <TableHead>Overall Score</TableHead>
                <TableHead>Status</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {appraisals.map((a) => (
                <TableRow key={a.id}>
                  <TableCell className="font-medium">{a.employee_name ?? `#${a.employee_id}`}</TableCell>
                  <TableCell>{a.period}</TableCell>
                  <TableCell>{a.self_rating ? `${a.self_rating}/5` : "—"}</TableCell>
                  <TableCell>{a.manager_rating ? `${a.manager_rating}/5` : "—"}</TableCell>
                  <TableCell>
                    <Badge variant="secondary">{overallScore(a)}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={appraisalStatusVariant(a.status)}>{a.status}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1 flex-wrap">
                      {a.status === "Pending" || a.status === "In Progress" ? (
                        <>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-7 text-xs text-green-600 hover:text-green-700 hover:bg-green-50"
                            onClick={async () => {
                              try {
                                await updateAppraisal(a.id, { status: "Approved" })
                                await load()
                                toast("Appraisal approved", "success")
                              } catch (e: unknown) {
                                toast(e instanceof Error ? e.message : "Failed", "error")
                              }
                            }}
                          >
                            <Check className="h-3 w-3 mr-1" /> Approve
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-7 text-xs text-destructive hover:bg-destructive/10"
                            onClick={async () => {
                              try {
                                await updateAppraisal(a.id, { status: "Rejected" })
                                await load()
                                toast("Appraisal rejected", "success")
                              } catch (e: unknown) {
                                toast(e instanceof Error ? e.message : "Failed", "error")
                              }
                            }}
                          >
                            <X className="h-3 w-3 mr-1" /> Reject
                          </Button>
                        </>
                      ) : null}
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 text-xs text-[var(--brand-color)]"
                        onClick={() => { setEditing(a); setEditStatus(a.status) }}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 text-xs text-destructive"
                        onClick={() => handleDelete(a.id)}
                      >
                        Delete
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
              {appraisals.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-muted-foreground italic py-8">
                    No appraisals found.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  )
}

// ---- Skills Tab ----
function SkillsTab() {
  const [skills, setSkills] = useState<Skill[]>([])
  const [employees, setEmployees] = useState<Employee[]>([])
  const [empSkills, setEmpSkills] = useState<EmployeeSkill[]>([])
  const [selectedEmpId, setSelectedEmpId] = useState("")
  const [loading, setLoading] = useState(true)
  const [empSkillsLoading, setEmpSkillsLoading] = useState(false)
  const [error, setError] = useState("")

  const [showAddSkill, setShowAddSkill] = useState(false)
  const [showAddEmpSkill, setShowAddEmpSkill] = useState(false)
  const [addSkillCategory, setAddSkillCategory] = useState("Software")
  const [addEmpSkillId, setAddEmpSkillId] = useState("")
  const [addEmpProficiency, setAddEmpProficiency] = useState("Beginner")

  const CATEGORIES = ["Software", "Hardware", "Soft Skills", "Domain Knowledge"]
  const PROFICIENCY_LEVELS = ["Beginner", "Intermediate", "Advanced", "Expert"]

  const load = useCallback(async () => {
    try {
      setError("")
      const [skillsData, empData] = await Promise.all([fetchSkills(), fetchEmployees()])
      setSkills(Array.isArray(skillsData) ? skillsData : [])
      setEmployees(Array.isArray(empData) ? empData : [])
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load skills")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  async function loadEmpSkills(empId: string) {
    if (!empId) { setEmpSkills([]); return }
    setEmpSkillsLoading(true)
    try {
      const data = await fetchEmployeeSkills(Number(empId))
      setEmpSkills(Array.isArray(data) ? data : [])
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : "Failed to load employee skills", "error")
    } finally {
      setEmpSkillsLoading(false)
    }
  }

  function handleSelectEmp(id: string) {
    setSelectedEmpId(id)
    loadEmpSkills(id)
  }

  async function handleAddSkill(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const fd = new FormData(e.currentTarget)
    try {
      await createSkill({
        name: fd.get("name") as string,
        category: addSkillCategory,
      })
      setShowAddSkill(false)
      setAddSkillCategory("Software")
      await load()
      toast("Skill added to library", "success")
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : "Failed to add skill", "error")
    }
  }

  async function handleAddEmpSkill(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    try {
      await addEmployeeSkill({
        employee_id: Number(selectedEmpId),
        skill_id: Number(addEmpSkillId),
        proficiency: addEmpProficiency,
      })
      setShowAddEmpSkill(false)
      setAddEmpSkillId("")
      setAddEmpProficiency("Beginner")
      await loadEmpSkills(selectedEmpId)
      toast("Skill assigned", "success")
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : "Failed to assign skill", "error")
    }
  }

  async function handleRemoveEmpSkill(id: number) {
    if (!confirm("Remove this skill from employee?")) return
    try {
      await deleteEmployeeSkill(id)
      await loadEmpSkills(selectedEmpId)
      toast("Skill removed", "success")
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : "Remove failed", "error")
    }
  }

  function proficiencyColor(level: string): string {
    switch (level.toLowerCase()) {
      case "expert": return "bg-green-100 text-green-800 border-green-200"
      case "advanced": return "bg-purple-100 text-purple-800 border-purple-200"
      case "intermediate": return "bg-blue-100 text-blue-800 border-blue-200"
      default: return "bg-gray-100 text-gray-700 border-gray-200"
    }
  }

  function categoryColor(cat: string): string {
    switch (cat) {
      case "Software": return "bg-blue-100 text-blue-700"
      case "Hardware": return "bg-orange-100 text-orange-700"
      case "Soft Skills": return "bg-pink-100 text-pink-700"
      case "Domain Knowledge": return "bg-teal-100 text-teal-700"
      default: return "bg-gray-100 text-gray-700"
    }
  }

  // Group skills by category
  const grouped = CATEGORIES.reduce<Record<string, Skill[]>>((acc, cat) => {
    acc[cat] = skills.filter((s) => s.category === cat)
    return acc
  }, {})
  const otherSkills = skills.filter((s) => !CATEGORIES.includes(s.category))
  if (otherSkills.length > 0) grouped["Other"] = otherSkills

  return (
    <div className="space-y-4">
      {error && <ErrorBox msg={error} />}

      {/* Add Skill to Library Dialog */}
      <Dialog open={showAddSkill} onOpenChange={(open) => { setShowAddSkill(open); if (!open) setAddSkillCategory("Software") }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Skill to Library</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleAddSkill}>
            <div className="space-y-4 py-4">
              <div className="space-y-1.5">
                <Label htmlFor="name">Skill Name *</Label>
                <Input name="name" required placeholder="e.g. React, Python, Negotiation" />
              </div>
              <div className="space-y-1.5">
                <Label>Category</Label>
                <Select value={addSkillCategory} onValueChange={setAddSkillCategory}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {CATEGORIES.map((c) => (
                      <SelectItem key={c} value={c}>{c}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <DialogClose asChild>
                <Button type="button" variant="outline">Cancel</Button>
              </DialogClose>
              <Button type="submit">Add Skill</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Add Employee Skill Dialog */}
      <Dialog open={showAddEmpSkill} onOpenChange={(open) => { setShowAddEmpSkill(open); if (!open) { setAddEmpSkillId(""); setAddEmpProficiency("Beginner") } }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Assign Skill</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleAddEmpSkill}>
            <div className="space-y-4 py-4">
              <div className="space-y-1.5">
                <Label>Skill *</Label>
                <Select value={addEmpSkillId} onValueChange={setAddEmpSkillId} required>
                  <SelectTrigger>
                    <SelectValue placeholder="Select skill" />
                  </SelectTrigger>
                  <SelectContent>
                    {skills.map((s) => (
                      <SelectItem key={s.id} value={String(s.id)}>{s.name} ({s.category})</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label>Proficiency</Label>
                <Select value={addEmpProficiency} onValueChange={setAddEmpProficiency}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {PROFICIENCY_LEVELS.map((p) => (
                      <SelectItem key={p} value={p}>{p}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <DialogClose asChild>
                <Button type="button" variant="outline">Cancel</Button>
              </DialogClose>
              <Button type="submit" disabled={!addEmpSkillId}>Assign Skill</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {loading ? (
        <Spinner />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Left Panel: Skills Library */}
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">Skills Library</CardTitle>
                <Button size="sm" onClick={() => setShowAddSkill(true)}>
                  <Plus className="h-4 w-4 mr-1" /> Add Skill
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {Object.entries(grouped).map(([cat, catSkills]) =>
                catSkills.length > 0 ? (
                  <div key={cat}>
                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-2">{cat}</p>
                    <div className="flex flex-wrap gap-2">
                      {catSkills.map((s) => (
                        <span
                          key={s.id}
                          className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${categoryColor(s.category)}`}
                        >
                          {s.name}
                        </span>
                      ))}
                    </div>
                  </div>
                ) : null
              )}
              {skills.length === 0 && (
                <p className="text-sm text-muted-foreground italic text-center py-4">
                  No skills in library yet.
                </p>
              )}
            </CardContent>
          </Card>

          {/* Right Panel: Employee Skills */}
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">Employee Skills</CardTitle>
                {selectedEmpId && (
                  <Button size="sm" onClick={() => setShowAddEmpSkill(true)}>
                    <Plus className="h-4 w-4 mr-1" /> Add Skill
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="space-y-1.5">
                <Label>Select Employee</Label>
                <Select value={selectedEmpId} onValueChange={handleSelectEmp}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose an employee..." />
                  </SelectTrigger>
                  <SelectContent>
                    {employees.map((emp) => (
                      <SelectItem key={emp.id} value={String(emp.id)}>{emp.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {empSkillsLoading ? (
                <Spinner />
              ) : !selectedEmpId ? (
                <p className="text-sm text-muted-foreground italic text-center py-4">
                  Select an employee to view their skills.
                </p>
              ) : empSkills.length === 0 ? (
                <p className="text-sm text-muted-foreground italic text-center py-4">
                  No skills assigned yet.
                </p>
              ) : (
                <div className="space-y-2">
                  {empSkills.map((es) => (
                    <div
                      key={es.id}
                      className="flex items-center justify-between rounded-lg border p-3"
                    >
                      <div className="space-y-1">
                        <p className="text-sm font-medium">{es.skill_name ?? `Skill #${es.skill_id}`}</p>
                        {es.skill_category && (
                          <span className={`inline-flex items-center px-1.5 py-0 rounded text-xs font-medium ${categoryColor(es.skill_category)}`}>
                            {es.skill_category}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded border text-xs font-semibold ${proficiencyColor(es.proficiency)}`}>
                          {es.proficiency}
                        </span>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 text-xs text-destructive px-2"
                          onClick={() => handleRemoveEmpSkill(es.id)}
                        >
                          ×
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

// ---- Leave Tab ----
// Month/year select helpers for Safari-safe date input
function DateSelects({ namePrefix, label }: { namePrefix: string; label: string }) {
  const currentYear = new Date().getFullYear()
  const years = [currentYear - 1, currentYear, currentYear + 1]
  const months = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
  ]
  const days = Array.from({ length: 31 }, (_, i) => i + 1)
  return (
    <div className="space-y-1.5">
      <Label>{label} *</Label>
      <div className="flex gap-1">
        <select name={`${namePrefix}_day`} className="flex-1 h-9 rounded-md border border-input px-2 text-sm bg-background" required>
          <option value="">Day</option>
          {days.map(d => <option key={d} value={String(d).padStart(2,"0")}>{d}</option>)}
        </select>
        <select name={`${namePrefix}_month`} className="flex-1 h-9 rounded-md border border-input px-2 text-sm bg-background" required>
          <option value="">Month</option>
          {months.map((m, i) => <option key={m} value={String(i+1).padStart(2,"0")}>{m}</option>)}
        </select>
        <select name={`${namePrefix}_year`} className="flex-1 h-9 rounded-md border border-input px-2 text-sm bg-background" required>
          <option value="">Year</option>
          {years.map(y => <option key={y} value={String(y)}>{y}</option>)}
        </select>
      </div>
    </div>
  )
}

function leaveDate(fd: FormData, prefix: string): string {
  const y = fd.get(`${prefix}_year`) as string
  const m = fd.get(`${prefix}_month`) as string
  const d = fd.get(`${prefix}_day`) as string
  return `${y}-${m}-${d}`
}

function LeaveTab() {
  const [requests, setRequests] = useState<LeaveRequest[]>([])
  const [employees, setEmployees] = useState<Employee[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [showAdd, setShowAdd] = useState(false)
  const [showYearEnd, setShowYearEnd] = useState(false)
  const [addEmployeeId, setAddEmployeeId] = useState("")
  const [addLeaveType, setAddLeaveType] = useState("Sick")
  const [selectedBalance, setSelectedBalance] = useState<LeaveBalance | null>(null)
  const [lopWarning, setLopWarning] = useState<string | null>(null)
  const [yearEndResults, setYearEndResults] = useState<{ employee_id: number; personal_unused: number; carry_forward: number; payout_days: number; payout_amount: number }[]>([])

  const LEAVE_TYPES = ["Sick", "Personal", "Unpaid", "Other"]
  const currentYear = new Date().getFullYear()

  const load = useCallback(async () => {
    try {
      setError("")
      const [leavesData, empData] = await Promise.all([fetchLeaveRequests(), fetchEmployees()])
      setRequests(Array.isArray(leavesData) ? leavesData : [])
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const empResult = empData as any
      setEmployees(Array.isArray(empResult) ? empResult : (empResult?.employees ?? []))
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load leave requests")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  // Load balance when employee or leave type changes (for Sick/Personal only)
  useEffect(() => {
    setLopWarning(null)
    setSelectedBalance(null)
    if (!addEmployeeId || !["Sick", "Personal"].includes(addLeaveType)) return
    fetchLeaveBalance(Number(addEmployeeId), currentYear).then(setSelectedBalance).catch(() => null)
  }, [addEmployeeId, addLeaveType, currentYear])

  function computeLopWarning(fd: FormData): void {
    if (!["Sick", "Personal"].includes(addLeaveType)) { setLopWarning(null); return }
    const start = leaveDate(fd, "start")
    const end = leaveDate(fd, "end")
    if (!start.match(/^\d{4}-\d{2}-\d{2}$/) || !end.match(/^\d{4}-\d{2}-\d{2}$/)) return
    const days = countDays(start, end)
    if (!selectedBalance) return

    const quota = addLeaveType === "Sick"
      ? selectedBalance.sick_total - selectedBalance.sick_used
      : (selectedBalance.personal_total + selectedBalance.personal_carried) - selectedBalance.personal_used

    const lop = Math.max(0, days - quota)
    if (lop > 0) {
      setLopWarning(`⚠ ${lop} day${lop > 1 ? "s" : ""} exceed${lop === 1 ? "s" : ""} quota — ₹${lop * LEAVE_RATE} loss of pay will apply.`)
    } else {
      setLopWarning(null)
    }
  }

  async function handleAdd(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const fd = new FormData(e.currentTarget)
    const start = leaveDate(fd, "start")
    const end = leaveDate(fd, "end")

    // No clubbing check: prevent Sick+Personal overlap
    if (["Sick", "Personal"].includes(addLeaveType)) {
      const otherType = addLeaveType === "Sick" ? "Personal" : "Sick"
      const overlap = requests.find(r =>
        r.employee_id === Number(addEmployeeId) &&
        r.leave_type === otherType &&
        r.status !== "Rejected" &&
        !(end < r.start_date || start > r.end_date)
      )
      if (overlap) {
        toast(`Cannot overlap with existing ${otherType} leave (${overlap.start_date} – ${overlap.end_date}). Sick and Personal leaves cannot be clubbed.`, "error")
        return
      }
    }

    try {
      await createLeaveRequest({
        employee_id: Number(addEmployeeId),
        leave_type: addLeaveType,
        start_date: start,
        end_date: end,
        reason: fd.get("reason") as string,
      })
      setShowAdd(false)
      setAddEmployeeId("")
      setAddLeaveType("Sick")
      setLopWarning(null)
      setSelectedBalance(null)
      await load()
      toast("Leave request submitted", "success")
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : "Failed to submit", "error")
    }
  }

  async function handleApprove(r: LeaveRequest) {
    try {
      await updateLeaveRequestStatus(r.id, "Approved")
      // Apply to balance and check for LOP
      if (["Sick", "Personal"].includes(r.leave_type)) {
        const days = countDays(r.start_date, r.end_date)
        const year = new Date(r.start_date).getFullYear()
        const { lop_days, lop_amount } = await applyLeaveToBalance(
          r.employee_id, r.id, r.leave_type as "Sick" | "Personal", days, year
        )
        if (lop_days > 0) {
          toast(`Approved. ${lop_days} day${lop_days > 1 ? "s" : ""} over quota → ₹${lop_amount} loss of pay recorded.`, "success")
        } else {
          toast("Leave approved", "success")
        }
      } else {
        toast("Leave approved", "success")
      }
      await load()
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : "Failed", "error")
    }
  }

  async function handleReject(id: number) {
    try {
      await updateLeaveRequestStatus(id, "Rejected")
      await load()
      toast("Leave rejected", "success")
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : "Failed", "error")
    }
  }

  async function handleDelete(id: number) {
    if (!confirm("Delete this leave request?")) return
    try {
      await deleteLeaveRequest(id)
      await load()
      toast("Deleted", "success")
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : "Delete failed", "error")
    }
  }

  async function handleYearEnd() {
    try {
      const results = await processYearEndLeave(currentYear)
      setYearEndResults(results)
      setShowYearEnd(true)
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : "Year-end processing failed", "error")
    }
  }

  function statusVariant(status: string): "default" | "secondary" | "destructive" | "outline" {
    if (status === "Approved") return "default"
    if (status === "Rejected") return "destructive"
    return "outline"
  }

  function balanceBadge(b: LeaveBalance | null, type: "sick" | "personal") {
    if (!b) return null
    const used = type === "sick" ? b.sick_used : b.personal_used
    const total = type === "sick" ? b.sick_total : b.personal_total + b.personal_carried
    const remaining = total - used
    const variant = remaining <= 0 ? "destructive" : remaining <= 2 ? "secondary" : "outline"
    return <Badge variant={variant} className="text-xs">{remaining}/{total} left</Badge>
  }

  const pending = requests.filter((r) => r.status === "Pending").length

  return (
    <div className="space-y-4">
      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-3 text-sm">
        <Card><CardContent className="p-3">
          <p className="text-xs text-muted-foreground">Sick Leave</p>
          <p className="font-semibold">{SICK_QUOTA} days / year</p>
          <p className="text-xs text-muted-foreground">Expires year-end</p>
        </CardContent></Card>
        <Card><CardContent className="p-3">
          <p className="text-xs text-muted-foreground">Personal Leave</p>
          <p className="font-semibold">{PERSONAL_QUOTA} days / year</p>
          <p className="text-xs text-muted-foreground">Carry forward (max {PERSONAL_CARRY_CAP})</p>
        </CardContent></Card>
        <Card><CardContent className="p-3">
          <p className="text-xs text-muted-foreground">Loss of Pay Rate</p>
          <p className="font-semibold">₹{LEAVE_RATE} / day</p>
          <p className="text-xs text-muted-foreground">Applied on quota exceeded</p>
        </CardContent></Card>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {requests.length} requests{pending > 0 && <span className="ml-2 text-orange-600 font-medium">({pending} pending)</span>}
        </p>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleYearEnd}>Year-End Payout</Button>
          <Button onClick={() => setShowAdd(true)} size="sm">
            <Plus className="h-4 w-4 mr-1" /> New Request
          </Button>
        </div>
      </div>

      {error && <ErrorBox msg={error} />}

      {/* New Request Dialog */}
      <Dialog open={showAdd} onOpenChange={(open) => {
        setShowAdd(open)
        if (!open) { setAddEmployeeId(""); setAddLeaveType("Sick"); setLopWarning(null); setSelectedBalance(null) }
      }}>
        <DialogContent>
          <DialogHeader><DialogTitle>New Leave Request</DialogTitle></DialogHeader>
          <form onSubmit={handleAdd} onChange={(e) => computeLopWarning(new FormData(e.currentTarget))}>
            <div className="space-y-4 py-4">
              <div className="space-y-1.5">
                <Label>Employee *</Label>
                <Select value={addEmployeeId} onValueChange={setAddEmployeeId} required>
                  <SelectTrigger><SelectValue placeholder="Select employee" /></SelectTrigger>
                  <SelectContent>
                    {employees.map((emp) => (
                      <SelectItem key={emp.id} value={String(emp.id)}>{emp.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label>Leave Type</Label>
                <Select value={addLeaveType} onValueChange={setAddLeaveType}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {LEAVE_TYPES.map((t) => <SelectItem key={t} value={t}>{t}</SelectItem>)}
                  </SelectContent>
                </Select>
                {selectedBalance && (
                  <div className="flex gap-2 mt-1">
                    {addLeaveType === "Sick" && <>{balanceBadge(selectedBalance, "sick")} <span className="text-xs text-muted-foreground">Sick</span></>}
                    {addLeaveType === "Personal" && <>{balanceBadge(selectedBalance, "personal")} <span className="text-xs text-muted-foreground">Personal</span></>}
                  </div>
                )}
              </div>
              <div className="grid grid-cols-2 gap-4">
                <DateSelects namePrefix="start" label="Start Date" />
                <DateSelects namePrefix="end" label="End Date" />
              </div>
              {lopWarning && (
                <div className="rounded-md bg-orange-50 border border-orange-200 p-3 text-sm text-orange-700">{lopWarning}</div>
              )}
              <div className="space-y-1.5">
                <Label>Reason</Label>
                <Input name="reason" placeholder="Optional reason" />
              </div>
            </div>
            <DialogFooter>
              <DialogClose asChild><Button type="button" variant="outline">Cancel</Button></DialogClose>
              <Button type="submit" disabled={!addEmployeeId}>Submit Request</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Year-End Results Dialog */}
      <Dialog open={showYearEnd} onOpenChange={setShowYearEnd}>
        <DialogContent className="max-w-2xl">
          <DialogHeader><DialogTitle>Year-End Leave Payout — {currentYear}</DialogTitle></DialogHeader>
          <div className="space-y-3 py-2">
            <p className="text-sm text-muted-foreground">
              Unused Personal leaves above {PERSONAL_CARRY_CAP} are paid out. Sick leaves expire. Carry forward seeded for {currentYear + 1}.
            </p>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Employee</TableHead>
                    <TableHead className="text-right">Unused Personal</TableHead>
                    <TableHead className="text-right">Carry Forward</TableHead>
                    <TableHead className="text-right">Paid Out (days)</TableHead>
                    <TableHead className="text-right">Payout (₹)</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {yearEndResults.map((r) => {
                    const emp = employees.find(e => e.id === r.employee_id)
                    return (
                      <TableRow key={r.employee_id}>
                        <TableCell>{emp?.name ?? `#${r.employee_id}`}</TableCell>
                        <TableCell className="text-right">{r.personal_unused}</TableCell>
                        <TableCell className="text-right">{r.carry_forward}</TableCell>
                        <TableCell className="text-right">{r.payout_days}</TableCell>
                        <TableCell className="text-right font-medium">
                          {r.payout_amount > 0 ? `₹${r.payout_amount}` : "—"}
                        </TableCell>
                      </TableRow>
                    )
                  })}
                  {yearEndResults.length === 0 && (
                    <TableRow><TableCell colSpan={5} className="text-center text-muted-foreground py-6">No data</TableCell></TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          </div>
          <DialogFooter>
            <DialogClose asChild><Button>Close</Button></DialogClose>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {loading ? <Spinner /> : (
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Employee</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Dates</TableHead>
                <TableHead>Days</TableHead>
                <TableHead>Reason</TableHead>
                <TableHead>Status</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {requests.map((r) => (
                <TableRow key={r.id}>
                  <TableCell className="font-medium">{r.employee_name ?? `#${r.employee_id}`}</TableCell>
                  <TableCell>
                    <Badge variant="outline" className="text-xs">{r.leave_type}</Badge>
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {r.start_date} → {r.end_date}
                  </TableCell>
                  <TableCell className="text-xs">{countDays(r.start_date, r.end_date)}</TableCell>
                  <TableCell className="text-xs text-muted-foreground max-w-[140px] truncate">{r.reason || "—"}</TableCell>
                  <TableCell><Badge variant={statusVariant(r.status)}>{r.status}</Badge></TableCell>
                  <TableCell>
                    <div className="flex gap-1 flex-wrap">
                      {r.status === "Pending" && (
                        <>
                          <Button variant="ghost" size="sm" className="h-7 text-xs text-green-600 hover:text-green-700 hover:bg-green-50"
                            onClick={() => handleApprove(r)}>
                            <Check className="h-3 w-3 mr-1" /> Approve
                          </Button>
                          <Button variant="ghost" size="sm" className="h-7 text-xs text-destructive hover:bg-destructive/10"
                            onClick={() => handleReject(r.id)}>
                            <X className="h-3 w-3 mr-1" /> Reject
                          </Button>
                        </>
                      )}
                      <Button variant="ghost" size="sm" className="h-7 text-xs text-destructive"
                        onClick={() => handleDelete(r.id)}>Delete</Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
              {requests.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-muted-foreground italic py-8">No leave requests found.</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  )
}

// ---- Main Page ----
export default function HRPage() {
  const [activeTab, setActiveTab] = useState<Tab>("employees")

  const tabs: { key: Tab; label: string; icon: React.ReactNode }[] = [
    { key: "employees", label: "Employees", icon: <Users className="h-4 w-4" /> },
    { key: "payroll", label: "Payroll", icon: <DollarSign className="h-4 w-4" /> },
    { key: "goals", label: "Goals", icon: <Target className="h-4 w-4" /> },
    { key: "appraisals", label: "Appraisals", icon: <Star className="h-4 w-4" /> },
    { key: "skills", label: "Skills", icon: <Zap className="h-4 w-4" /> },
    { key: "leave", label: "Leave", icon: <CalendarDays className="h-4 w-4" /> },
  ]

  return (
    <AppLayout activePage="hr">
      <div className="px-4 py-4 md:px-6 md:py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold">Human Resources</h1>
          <p className="text-sm text-muted-foreground">Employee records, goals, appraisals and skills</p>
        </div>

        {/* Tab Bar */}
        <div className="flex gap-1 mb-6 bg-white rounded-xl p-1 shadow-sm w-fit border border-border flex-wrap">
          {tabs.map((t) => (
            <button
              key={t.key}
              onClick={() => setActiveTab(t.key)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                activeTab === t.key
                  ? "text-white"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted"
              }`}
              style={activeTab === t.key ? { backgroundColor: "var(--brand-color)" } : undefined}
            >
              {t.icon}
              {t.label}
            </button>
          ))}
        </div>

        <Card>
          <CardContent className="p-6">
            {activeTab === "employees" && <EmployeesTab />}
            {activeTab === "payroll" && <PayrollTab />}
            {activeTab === "goals" && <GoalsTab />}
            {activeTab === "appraisals" && <AppraisalsTab />}
            {activeTab === "skills" && <SkillsTab />}
            {activeTab === "leave" && <LeaveTab />}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
