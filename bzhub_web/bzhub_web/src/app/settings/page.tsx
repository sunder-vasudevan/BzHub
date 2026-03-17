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
import { Building2, User, Info, CheckCircle2, XCircle, Coins, LayoutTemplate, Sliders, Plus, Trash2 } from "lucide-react"
import { TEMPLATES, getActiveTemplate, applyTemplate, IndustryTemplate } from "@/lib/templates"
import {
  loadCustomFields,
  saveCustomFields,
  labelToId,
  ENTITY_LABELS,
  FIELD_TYPE_LABELS,
  type EntityType,
  type FieldType,
  type CustomField,
  type CustomFieldSchema,
} from "@/lib/customFields"

const ENTITY_TYPES: EntityType[] = ['employee', 'contact', 'lead', 'product']
const FIELD_TYPES: FieldType[] = ['text', 'number', 'date', 'boolean', 'dropdown', 'email', 'phone', 'url']

function CustomFieldsCard() {
  const [schema, setSchema] = useState<CustomFieldSchema>(() => loadCustomFields())
  const [activeEntity, setActiveEntity] = useState<EntityType>('employee')
  const [showAddForm, setShowAddForm] = useState(false)
  const [newLabel, setNewLabel] = useState('')
  const [newType, setNewType] = useState<FieldType>('text')
  const [newRequired, setNewRequired] = useState(false)
  const [newOptions, setNewOptions] = useState('')
  const [saved, setSaved] = useState(false)

  const fields = schema[activeEntity] ?? []

  function handleAddField() {
    if (!newLabel.trim()) return
    const id = labelToId(newLabel)
    if (fields.some(f => f.id === id)) {
      alert(`A field with id "${id}" already exists on this entity.`)
      return
    }
    const field: CustomField = {
      id,
      label: newLabel.trim(),
      type: newType,
      required: newRequired,
      options: newType === 'dropdown'
        ? newOptions.split(',').map(s => s.trim()).filter(Boolean)
        : undefined,
    }
    const updated = { ...schema, [activeEntity]: [...fields, field] }
    setSchema(updated)
    saveCustomFields(updated)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
    setShowAddForm(false)
    setNewLabel('')
    setNewType('text')
    setNewRequired(false)
    setNewOptions('')
  }

  function handleDelete(id: string) {
    const updated = { ...schema, [activeEntity]: fields.filter(f => f.id !== id) }
    setSchema(updated)
    saveCustomFields(updated)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Sliders className="h-4 w-4" style={{ color: "var(--brand-color)" }} />
          Custom Fields
          {saved && (
            <span className="ml-auto text-xs text-emerald-600 flex items-center gap-1 font-normal">
              <CheckCircle2 className="h-3.5 w-3.5" /> Saved
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground mb-4">
          Add extra fields to any entity. They appear in the add/edit forms for that module.
        </p>

        {/* Entity tabs */}
        <div className="flex gap-1 mb-4 flex-wrap">
          {ENTITY_TYPES.map(et => (
            <button
              key={et}
              onClick={() => { setActiveEntity(et); setShowAddForm(false) }}
              className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                activeEntity === et
                  ? 'text-white'
                  : 'bg-muted text-muted-foreground hover:text-foreground'
              }`}
              style={activeEntity === et ? { backgroundColor: 'var(--brand-color)' } : {}}
            >
              {ENTITY_LABELS[et]}
            </button>
          ))}
        </div>

        {/* Field list */}
        {fields.length === 0 && !showAddForm && (
          <p className="text-sm text-muted-foreground py-4 text-center border border-dashed rounded-lg">
            No custom fields for {ENTITY_LABELS[activeEntity]} yet
          </p>
        )}
        {fields.length > 0 && (
          <div className="space-y-2 mb-4">
            {fields.map(field => (
              <div
                key={field.id}
                className="flex items-center gap-2 px-3 py-2 rounded-lg border border-border bg-muted/30"
              >
                <div className="flex-1 min-w-0">
                  <span className="text-sm font-medium">{field.label}</span>
                  {field.required && (
                    <span className="text-destructive text-xs ml-1">*</span>
                  )}
                </div>
                <Badge variant="secondary" className="text-xs shrink-0">
                  {FIELD_TYPE_LABELS[field.type]}
                </Badge>
                {field.type === 'dropdown' && field.options?.length && (
                  <span className="text-xs text-muted-foreground shrink-0">
                    {field.options.length} options
                  </span>
                )}
                <button
                  onClick={() => handleDelete(field.id)}
                  className="text-muted-foreground hover:text-destructive transition-colors shrink-0"
                  title="Remove field"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Add field form */}
        {showAddForm ? (
          <div className="border rounded-lg p-4 space-y-3 bg-muted/20">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              New field — {ENTITY_LABELS[activeEntity]}
            </p>
            <div className="space-y-1.5">
              <Label className="text-xs">Field Label *</Label>
              <Input
                value={newLabel}
                onChange={e => setNewLabel(e.target.value)}
                placeholder="e.g. Blood Type"
                autoFocus
              />
              {newLabel && (
                <p className="text-xs text-muted-foreground">
                  Key: <code className="bg-muted px-1 rounded">{labelToId(newLabel)}</code>
                </p>
              )}
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label className="text-xs">Field Type</Label>
                <select
                  value={newType}
                  onChange={e => setNewType(e.target.value as FieldType)}
                  className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm"
                >
                  {FIELD_TYPES.map(t => (
                    <option key={t} value={t}>{FIELD_TYPE_LABELS[t]}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs">Required?</Label>
                <div className="flex items-center gap-2 h-9">
                  <input
                    type="checkbox"
                    id="cf_required"
                    checked={newRequired}
                    onChange={e => setNewRequired(e.target.checked)}
                    className="h-4 w-4 rounded border-input"
                  />
                  <Label htmlFor="cf_required" className="text-sm cursor-pointer">Required field</Label>
                </div>
              </div>
            </div>
            {newType === 'dropdown' && (
              <div className="space-y-1.5">
                <Label className="text-xs">Options (comma-separated)</Label>
                <Input
                  value={newOptions}
                  onChange={e => setNewOptions(e.target.value)}
                  placeholder="e.g. A+, B+, O+, AB+"
                />
              </div>
            )}
            <div className="flex gap-2 pt-1">
              <Button
                size="sm"
                onClick={handleAddField}
                disabled={!newLabel.trim()}
                style={{ backgroundColor: "var(--brand-color)" }}
                className="text-white hover:opacity-90"
              >
                Add Field
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => { setShowAddForm(false); setNewLabel(''); setNewType('text'); setNewRequired(false); setNewOptions('') }}
              >
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <Button
            size="sm"
            variant="outline"
            onClick={() => setShowAddForm(true)}
            className="gap-1"
          >
            <Plus className="h-4 w-4" />
            Add Field
          </Button>
        )}
      </CardContent>
    </Card>
  )
}

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

  // Industry template state
  const [activeTemplate, setActiveTemplate] = useState<IndustryTemplate>(() =>
    typeof window !== 'undefined' ? getActiveTemplate() : TEMPLATES[0]
  )
  const [templateSaved, setTemplateSaved] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem("bzhub_currency")
    if (stored) setCurrency(stored)
  }, [])

  function handleSelectTemplate(t: IndustryTemplate) {
    applyTemplate(t)
    setActiveTemplate(t)
    setTemplateSaved(true)
    setTimeout(() => setTemplateSaved(false), 3000)
  }

  function handleSaveCurrency() {
    localStorage.setItem("bzhub_currency", currency)
    window.dispatchEvent(new Event("bzhub_currency_changed"))
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
        if (data?.company_name) {
          localStorage.setItem("bzhub_company_name", data.company_name)
          window.dispatchEvent(new Event("bzhub_company_changed"))
        }
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
      if (data.company_name) {
        localStorage.setItem("bzhub_company_name", data.company_name)
        window.dispatchEvent(new Event("bzhub_company_changed"))
      }
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
                <Building2 className="h-4 w-4" style={{ color: "var(--brand-color)" }} />
                Company Profile
              </CardTitle>
            </CardHeader>
            <CardContent>
              {companyLoading ? (
                <div className="flex items-center justify-center py-10">
                  <div
                    className="h-7 w-7 rounded-full border-4 border-t-transparent animate-spin"
                    style={{ borderColor: "var(--brand-color)", borderTopColor: "transparent" }}
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
                      style={{ backgroundColor: "var(--brand-color)" }}
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
                <Coins className="h-4 w-4" style={{ color: "var(--brand-color)" }} />
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
                    style={{ backgroundColor: "var(--brand-color)" }}
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

          {/* Industry Template Card */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <LayoutTemplate className="h-4 w-4" style={{ color: "var(--brand-color)" }} />
                Industry Template
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                Choose a template to pre-configure your dashboard KPIs for your industry. You can still customise further from the Dashboard.
              </p>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {TEMPLATES.map((t) => {
                  const isActive = activeTemplate.id === t.id
                  return (
                    <button
                      key={t.id}
                      onClick={() => handleSelectTemplate(t)}
                      className={`text-left rounded-lg border-2 p-4 transition-all hover:shadow-sm ${
                        isActive ? "border-current" : "border-border hover:border-muted-foreground/50"
                      }`}
                      style={isActive ? { borderColor: t.color } : {}}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <span className="font-medium text-sm">{t.name}</span>
                        {isActive && (
                          <CheckCircle2 className="h-4 w-4 flex-shrink-0" style={{ color: t.color }} />
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground mb-3 leading-relaxed">{t.description}</p>
                      <ul className="space-y-1">
                        {t.highlights.map((h) => (
                          <li key={h} className="text-xs text-muted-foreground flex items-center gap-1.5">
                            <span className="h-1 w-1 rounded-full flex-shrink-0" style={{ backgroundColor: t.color }} />
                            {h}
                          </li>
                        ))}
                      </ul>
                    </button>
                  )
                })}
              </div>
              {templateSaved && (
                <div className="flex items-center gap-2 mt-4 text-sm text-emerald-600">
                  <CheckCircle2 className="h-4 w-4" />
                  Template applied — dashboard KPIs updated
                </div>
              )}
            </CardContent>
          </Card>

          {/* Custom Fields Card */}
          <CustomFieldsCard />

          {/* Current User Card */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <User className="h-4 w-4" style={{ color: "var(--brand-color)" }} />
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
                <Info className="h-4 w-4" style={{ color: "var(--brand-color)" }} />
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
                          style={{ borderColor: "var(--brand-color)", borderTopColor: "transparent" }}
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
