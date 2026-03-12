"use client"

import { useEffect, useState, useCallback } from "react"
import AppLayout from "@/components/layout/AppLayout"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { fetchAuditLogs } from "@/lib/db"
import type { AuditLog } from "@/lib/db"
import { ClipboardCheck, RefreshCw } from "lucide-react"

function actionBadge(action: string) {
  switch (action) {
    case "create":
      return <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200 hover:bg-emerald-100">Create</Badge>
    case "update":
      return <Badge className="bg-blue-100 text-blue-700 border-blue-200 hover:bg-blue-100">Update</Badge>
    case "delete":
      return <Badge className="bg-red-100 text-red-700 border-red-200 hover:bg-red-100">Delete</Badge>
    default:
      return <Badge variant="secondary">{action}</Badge>
  }
}

function formatDateTime(ts: string) {
  try {
    return new Date(ts).toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  } catch {
    return ts
  }
}

export default function AuditLogPage() {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [actionFilter, setActionFilter] = useState("all")
  const [moduleFilter, setModuleFilter] = useState("all")

  const load = useCallback(async () => {
    try {
      setError("")
      setLoading(true)
      const data = await fetchAuditLogs(200)
      setLogs(data)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load audit logs")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  // Derive unique modules from logs
  const allModules = Array.from(new Set(logs.map(l => l.table_name))).sort()

  const filtered = logs.filter(log => {
    const matchAction = actionFilter === "all" || log.action === actionFilter
    const matchModule = moduleFilter === "all" || log.table_name === moduleFilter
    return matchAction && matchModule
  })

  return (
    <AppLayout activePage="audit-log">
      <div className="px-4 py-4 md:px-6 md:py-8">
        {/* Header */}
        <div className="flex items-start justify-between mb-6 gap-4 flex-wrap">
          <div className="flex items-center gap-3">
            <div
              className="h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0"
              style={{ backgroundColor: "color-mix(in srgb, var(--brand-color) 12%, transparent)" }}
            >
              <ClipboardCheck className="h-5 w-5" style={{ color: "var(--brand-color)" }} />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Audit Log</h1>
              <p className="text-sm text-muted-foreground">Track all create, update, and delete actions</p>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={load} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-destructive/10 border border-destructive/20 text-destructive rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* Filters */}
        <div className="flex items-center gap-3 mb-4 flex-wrap">
          <Select value={actionFilter} onValueChange={setActionFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Action" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Actions</SelectItem>
              <SelectItem value="create">Create</SelectItem>
              <SelectItem value="update">Update</SelectItem>
              <SelectItem value="delete">Delete</SelectItem>
            </SelectContent>
          </Select>

          <Select value={moduleFilter} onValueChange={setModuleFilter}>
            <SelectTrigger className="w-44">
              <SelectValue placeholder="Module" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Modules</SelectItem>
              {allModules.map(m => (
                <SelectItem key={m} value={m}>{m}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          {(actionFilter !== "all" || moduleFilter !== "all") && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => { setActionFilter("all"); setModuleFilter("all") }}
            >
              Clear filters
            </Button>
          )}

          <span className="text-xs text-muted-foreground ml-auto">
            {filtered.length} {filtered.length === 1 ? "entry" : "entries"}
          </span>
        </div>

        <Card>
          <CardContent className="p-0">
            {loading ? (
              <div className="flex items-center justify-center py-20">
                <div
                  className="h-8 w-8 rounded-full border-4 border-t-transparent animate-spin"
                  style={{ borderColor: "var(--brand-color)", borderTopColor: "transparent" }}
                />
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date / Time</TableHead>
                      <TableHead>Module</TableHead>
                      <TableHead>Action</TableHead>
                      <TableHead>Record ID</TableHead>
                      <TableHead>Summary</TableHead>
                      <TableHead>Changed By</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filtered.map(log => (
                      <TableRow key={log.id}>
                        <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
                          {formatDateTime(log.created_at)}
                        </TableCell>
                        <TableCell>
                          <span className="text-xs font-medium bg-muted px-2 py-0.5 rounded">
                            {log.table_name}
                          </span>
                        </TableCell>
                        <TableCell>{actionBadge(log.action)}</TableCell>
                        <TableCell className="text-xs text-muted-foreground">{log.record_id}</TableCell>
                        <TableCell className="text-sm max-w-xs truncate">{log.summary}</TableCell>
                        <TableCell className="text-sm">{log.changed_by}</TableCell>
                      </TableRow>
                    ))}
                    {filtered.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={6} className="text-center text-muted-foreground italic py-12">
                          {logs.length === 0
                            ? "No audit log entries yet. Actions you take will appear here."
                            : "No entries match the current filters."}
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
