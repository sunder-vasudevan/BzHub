"use client"

import { useEffect, useState, useCallback } from "react"
import AppLayout from "@/components/layout/AppLayout"
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
  fetchEmployees,
  createEmployee,
  updateEmployee,
  deleteEmployee,
  fetchPayrolls,
} from "@/lib/api"
import { Plus, Users, DollarSign } from "lucide-react"

type Tab = "employees" | "payroll"

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

// ---- Employees Tab ----
function EmployeesTab() {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [showAdd, setShowAdd] = useState(false)
  const [editing, setEditing] = useState<Employee | null>(null)

  const load = useCallback(async () => {
    try {
      setError("")
      const data = await fetchEmployees()
      // API may return { employees: [...] } or a plain array
      const list = Array.isArray(data) ? data : (data?.employees ?? [])
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
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : "Delete failed")
    }
  }

  async function handleSave(e: React.FormEvent<HTMLFormElement>, employeeId?: number) {
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
      if (employeeId) {
        await updateEmployee(employeeId, data)
        setEditing(null)
      } else {
        await createEmployee(data)
        setShowAdd(false)
      }
      await load()
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : "Save failed")
    }
  }

  function isActive(emp: Employee): boolean {
    if (emp.is_active === undefined || emp.is_active === null) return true
    if (typeof emp.is_active === "boolean") return emp.is_active
    return emp.is_active !== 0
  }

  function EmployeeForm({ emp, onClose }: { emp?: Employee; onClose: () => void }) {
    return (
      <form onSubmit={(e) => handleSave(e, emp?.id)}>
        <div className="grid grid-cols-2 gap-4 py-4">
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
        <Button onClick={() => setShowAdd(true)} size="sm">
          <Plus className="h-4 w-4 mr-1" /> Add Employee
        </Button>
      </div>

      {error && (
        <div className="p-3 bg-destructive/10 border border-destructive/20 text-destructive rounded-lg text-sm">
          {error}
        </div>
      )}

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
        <div className="flex items-center justify-center py-20">
          <div
            className="h-8 w-8 rounded-full border-4 border-t-transparent animate-spin"
            style={{ borderColor: "#6D28D9", borderTopColor: "transparent" }}
          />
        </div>
      ) : (
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
                      className="h-7 text-xs text-[#6D28D9]"
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
      )}
    </div>
  )
}

// ---- Payroll Tab ----
function PayrollTab() {
  const [records, setRecords] = useState<PayrollRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    fetchPayrolls()
      .then((data) => {
        const list = Array.isArray(data) ? data : (data?.payrolls ?? [])
        setRecords(list)
      })
      .catch((e: unknown) => {
        setError(e instanceof Error ? e.message : "Failed to load payroll")
      })
      .finally(() => setLoading(false))
  }, [])

  // Total gross for this month
  const now = new Date()
  const thisMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`
  const monthRecords = records.filter((r) => {
    const period = r.period_start ?? ""
    return period.startsWith(thisMonth)
  })
  const monthTotal = monthRecords.reduce(
    (sum, r) => sum + Number(r.gross_pay || 0),
    0
  )

  function payrollStatusVariant(
    status?: string
  ): "default" | "secondary" | "destructive" | "outline" {
    if (!status) return "secondary"
    const s = status.toLowerCase()
    if (s === "paid") return "default"
    if (s === "draft") return "outline"
    return "secondary"
  }

  return (
    <div className="space-y-4">
      {/* Summary card */}
      <Card>
        <CardContent className="p-4 flex items-center gap-4">
          <div
            className="h-10 w-10 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{ backgroundColor: "#6D28D920" }}
          >
            <DollarSign className="h-5 w-5" style={{ color: "#6D28D9" }} />
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Total Payroll This Month</p>
            <p className="text-xl font-bold">${Number(monthTotal || 0).toFixed(2)}</p>
            <p className="text-xs text-muted-foreground">{monthRecords.length} records</p>
          </div>
        </CardContent>
      </Card>

      {error && (
        <div className="p-3 bg-destructive/10 border border-destructive/20 text-destructive rounded-lg text-sm">
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
                  {r.period_start && r.period_end
                    ? `${r.period_start} – ${r.period_end}`
                    : r.period_start ?? "—"}
                </TableCell>
                <TableCell className="text-right">
                  ${Number(r.gross_pay || 0).toFixed(2)}
                </TableCell>
                <TableCell className="text-right font-medium">
                  ${Number(r.net_pay || 0).toFixed(2)}
                </TableCell>
                <TableCell>
                  <Badge variant={payrollStatusVariant(r.status)}>
                    {r.status ?? "Draft"}
                  </Badge>
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
  ]

  return (
    <AppLayout activePage="hr">
      <div className="px-6 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold">Human Resources</h1>
          <p className="text-sm text-muted-foreground">Employee records and payroll management</p>
        </div>

        {/* Tab Bar */}
        <div className="flex gap-1 mb-6 bg-white rounded-xl p-1 shadow-sm w-fit border border-border">
          {tabs.map((t) => (
            <button
              key={t.key}
              onClick={() => setActiveTab(t.key)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                activeTab === t.key
                  ? "text-white"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted"
              }`}
              style={activeTab === t.key ? { backgroundColor: "#6D28D9" } : undefined}
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
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
