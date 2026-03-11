"use client"

import { useEffect, useState } from "react"
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
import { Separator } from "@/components/ui/separator"
import { fetchCompanySettings, saveCompanySettings, fetchHealth } from "@/lib/db"
import { Building2, User, Info, CheckCircle2, XCircle, Coins } from "lucide-react"

const CURRENCIES = [
  { symbol: "₹", label: "Indian Rupee (₹)" },
  { symbol: "$", label: "US Dollar ($)" },
  { symbol: "€", label: "Euro (€)" },
  { symbol: "£", label: "British Pound (£)" },
  { symbol: "¥", label: "Japanese Yen (¥)" },
  { symbol: "AED", label: "UAE Dirham (AED)" },
  { symbol: "SGD", label: "Singapore Dollar (SGD)" },
]

interface CompanyData extends Record<string, unknown> {
  company_name?: string
  address?: string
  phone?: string
  email?: string
  website?: string
}

export default function SettingsPage() {
  // Company profile state
  const [company, setCompany] = useState<CompanyData>({})
  const [companyLoading, setCompanyLoading] = useState(true)
  const [savingCompany, setSavingCompany] = useState(false)
  const [companySaved, setCompanySaved] = useState(false)
  const [companyError, setCompanyError] = useState("")

  // Current user state
  const [currentUser, setCurrentUser] = useState("")
  const [currentRole, setCurrentRole] = useState("")

  // Currency state — persisted in localStorage
  const [currency, setCurrency] = useState("₹")
  const [currencySaved, setCurrencySaved] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem("bzhub_currency")
    if (stored) setCurrency(stored)
  }, [])

  function handleSaveCurrency() {
    localStorage.setItem("bzhub_currency", currency)
    setCurrencySaved(true)
    setTimeout(() => setCurrencySaved(false), 3000)
  }

  // API health state
  const [apiStatus, setApiStatus] = useState<"checking" | "online" | "offline">("checking")
  const [apiVersion, setApiVersion] = useState("")

  // Load company settings from API
  useEffect(() => {
    fetchCompanySettings()
      .then((data: CompanyData) => {
        setCompany(data ?? {})
      })
      .catch(() => {
        // Endpoint may not exist yet — start with empty form
        setCompany({})
      })
      .finally(() => setCompanyLoading(false))
  }, [])

  // Read current user from localStorage (client-only)
  useEffect(() => {
    setCurrentUser(localStorage.getItem("bzhub_user") ?? "")
    setCurrentRole(localStorage.getItem("bzhub_role") ?? "")
  }, [])

  // Check API health
  useEffect(() => {
    fetchHealth()
      .then((data: { status?: string; version?: string }) => {
        setApiStatus("online")
        if (data?.version) setApiVersion(data.version)
      })
      .catch(() => setApiStatus("offline"))
  }, [])

  async function handleSaveCompany(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setSavingCompany(true)
    setCompanyError("")
    setCompanySaved(false)
    const fd = new FormData(e.currentTarget)
    const data: CompanyData = {
      company_name: fd.get("company_name") as string,
      address: fd.get("address") as string,
      phone: fd.get("phone") as string,
      email: fd.get("email") as string,
      website: fd.get("website") as string,
    }
    try {
      await saveCompanySettings(data)
      setCompany(data)
      setCompanySaved(true)
      setTimeout(() => setCompanySaved(false), 3000)
    } catch (e: unknown) {
      setCompanyError(e instanceof Error ? e.message : "Save failed")
    } finally {
      setSavingCompany(false)
    }
  }

  return (
    <AppLayout activePage="settings">
      <div className="px-6 py-8 max-w-2xl">
        <div className="mb-6">
          <h1 className="text-2xl font-bold">Settings</h1>
          <p className="text-sm text-muted-foreground">Company profile and application preferences</p>
        </div>

        <div className="space-y-6">
          {/* Company Profile Card */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Building2 className="h-4 w-4" style={{ color: "#6D28D9" }} />
                Company Profile
              </CardTitle>
            </CardHeader>
            <CardContent>
              {companyLoading ? (
                <div className="flex items-center justify-center py-10">
                  <div
                    className="h-7 w-7 rounded-full border-4 border-t-transparent animate-spin"
                    style={{ borderColor: "#6D28D9", borderTopColor: "transparent" }}
                  />
                </div>
              ) : (
                <form onSubmit={handleSaveCompany} className="space-y-4">
                  <div className="space-y-1.5">
                    <Label htmlFor="company_name">Company Name</Label>
                    <Input
                      id="company_name"
                      name="company_name"
                      defaultValue={company.company_name ?? ""}
                      placeholder="Acme Corp"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="address">Address</Label>
                    <Input
                      id="address"
                      name="address"
                      defaultValue={company.address ?? ""}
                      placeholder="123 Main St, City, State"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1.5">
                      <Label htmlFor="phone">Phone</Label>
                      <Input
                        id="phone"
                        name="phone"
                        defaultValue={company.phone ?? ""}
                        placeholder="+1 555 000 0000"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        name="email"
                        type="email"
                        defaultValue={company.email ?? ""}
                        placeholder="info@company.com"
                      />
                    </div>
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="website">Website</Label>
                    <Input
                      id="website"
                      name="website"
                      defaultValue={company.website ?? ""}
                      placeholder="https://company.com"
                    />
                  </div>

                  {companyError && (
                    <p className="text-sm text-destructive">{companyError}</p>
                  )}

                  <div className="flex items-center gap-3 pt-1">
                    <Button
                      type="submit"
                      disabled={savingCompany}
                      style={{ backgroundColor: "#6D28D9" }}
                      className="text-white hover:opacity-90"
                    >
                      {savingCompany ? "Saving…" : "Save Changes"}
                    </Button>
                    {companySaved && (
                      <span className="text-sm text-emerald-600 flex items-center gap-1">
                        <CheckCircle2 className="h-4 w-4" />
                        Saved
                      </span>
                    )}
                  </div>
                </form>
              )}
            </CardContent>
          </Card>

          {/* Currency Card */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Coins className="h-4 w-4" style={{ color: "#6D28D9" }} />
                Currency
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="space-y-1.5">
                  <Label htmlFor="currency">Currency Symbol</Label>
                  <select
                    id="currency"
                    value={currency}
                    onChange={(e) => setCurrency(e.target.value)}
                    className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  >
                    {CURRENCIES.map((c) => (
                      <option key={c.symbol} value={c.symbol}>{c.label}</option>
                    ))}
                  </select>
                </div>
                <div className="flex items-center gap-3 pt-1">
                  <Button
                    type="button"
                    onClick={handleSaveCurrency}
                    style={{ backgroundColor: "#6D28D9" }}
                    className="text-white hover:opacity-90"
                  >
                    Save Currency
                  </Button>
                  {currencySaved && (
                    <span className="text-sm text-emerald-600 flex items-center gap-1">
                      <CheckCircle2 className="h-4 w-4" />
                      Saved
                    </span>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Current User Card */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <User className="h-4 w-4" style={{ color: "#6D28D9" }} />
                Current User
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between py-2 border-b border-border">
                  <span className="text-sm text-muted-foreground">Username</span>
                  <span className="text-sm font-medium">{currentUser || "—"}</span>
                </div>
                <div className="flex items-center justify-between py-2">
                  <span className="text-sm text-muted-foreground">Role</span>
                  {currentRole ? (
                    <Badge variant="secondary" className="capitalize">
                      {currentRole}
                    </Badge>
                  ) : (
                    <span className="text-sm text-muted-foreground">—</span>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* App Info Card */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Info className="h-4 w-4" style={{ color: "#6D28D9" }} />
                Application Info
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between py-2 border-b border-border">
                  <span className="text-sm text-muted-foreground">Frontend Version</span>
                  <span className="text-sm font-medium">1.0.0</span>
                </div>
                {apiVersion && (
                  <div className="flex items-center justify-between py-2 border-b border-border">
                    <span className="text-sm text-muted-foreground">API Version</span>
                    <span className="text-sm font-medium">{apiVersion}</span>
                  </div>
                )}
                <Separator />
                <div className="flex items-center justify-between py-2">
                  <span className="text-sm text-muted-foreground">API Status</span>
                  <div className="flex items-center gap-1.5">
                    {apiStatus === "checking" && (
                      <>
                        <div
                          className="h-3.5 w-3.5 rounded-full border-2 border-t-transparent animate-spin"
                          style={{ borderColor: "#6D28D9", borderTopColor: "transparent" }}
                        />
                        <span className="text-xs text-muted-foreground">Checking…</span>
                      </>
                    )}
                    {apiStatus === "online" && (
                      <>
                        <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                        <Badge variant="secondary" className="text-emerald-700 bg-emerald-50 border-emerald-200">
                          Online
                        </Badge>
                      </>
                    )}
                    {apiStatus === "offline" && (
                      <>
                        <XCircle className="h-4 w-4 text-destructive" />
                        <Badge variant="destructive">Offline</Badge>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  )
}
