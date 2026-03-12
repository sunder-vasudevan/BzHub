"use client"

import { useEffect, useRef, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { Search, X, Package, Users, Briefcase, TrendingUp } from "lucide-react"
import { supabase } from "@/lib/supabase"

interface SearchResult {
  id: string
  category: "Inventory" | "Employee" | "Contact" | "Lead"
  title: string
  subtitle: string
  href: string
}

function categoryIcon(cat: SearchResult["category"]) {
  switch (cat) {
    case "Inventory": return <Package className="h-3.5 w-3.5" />
    case "Employee": return <Users className="h-3.5 w-3.5" />
    case "Contact": return <Briefcase className="h-3.5 w-3.5" />
    case "Lead": return <TrendingUp className="h-3.5 w-3.5" />
  }
}

function categoryColor(cat: SearchResult["category"]) {
  switch (cat) {
    case "Inventory": return "bg-blue-100 text-blue-700"
    case "Employee": return "bg-violet-100 text-violet-700"
    case "Contact": return "bg-emerald-100 text-emerald-700"
    case "Lead": return "bg-amber-100 text-amber-700"
  }
}

async function runSearch(query: string): Promise<SearchResult[]> {
  if (!query.trim()) return []

  const q = `%${query}%`

  const [invRes, empRes, contactRes, leadRes] = await Promise.all([
    supabase.from("inventory").select("item_name, quantity").ilike("item_name", q).limit(5),
    supabase.from("employees").select("id, name, designation").ilike("name", q).limit(5),
    supabase.from("crm_contacts").select("id, name, email").ilike("name", q).limit(5),
    supabase.from("crm_leads").select("id, title, company, stage").or(`title.ilike.${q},company.ilike.${q}`).limit(5),
  ])

  const results: SearchResult[] = []

  for (const item of invRes.data ?? []) {
    results.push({
      id: `inv-${item.item_name}`,
      category: "Inventory",
      title: item.item_name,
      subtitle: `${item.quantity} in stock`,
      href: "/operations",
    })
  }

  for (const emp of empRes.data ?? []) {
    results.push({
      id: `emp-${emp.id}`,
      category: "Employee",
      title: emp.name,
      subtitle: emp.designation ?? "Employee",
      href: "/hr",
    })
  }

  for (const contact of contactRes.data ?? []) {
    results.push({
      id: `contact-${contact.id}`,
      category: "Contact",
      title: contact.name,
      subtitle: contact.email ?? "No email",
      href: "/crm",
    })
  }

  for (const lead of leadRes.data ?? []) {
    results.push({
      id: `lead-${lead.id}`,
      category: "Lead",
      title: lead.title,
      subtitle: `${lead.company ?? "No company"} · ${lead.stage ?? ""}`,
      href: "/crm",
    })
  }

  return results
}

export default function GlobalSearch() {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const router = useRouter()
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Keyboard shortcut Cmd+K / Ctrl+K
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault()
        setOpen(prev => !prev)
      }
      if (e.key === "Escape") {
        setOpen(false)
      }
    }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [])

  // Focus input when opened
  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 50)
    } else {
      setQuery("")
      setResults([])
    }
  }, [open])

  const handleSearch = useCallback((value: string) => {
    setQuery(value)
    if (debounceRef.current) clearTimeout(debounceRef.current)
    if (!value.trim()) {
      setResults([])
      return
    }
    debounceRef.current = setTimeout(async () => {
      setLoading(true)
      try {
        const r = await runSearch(value)
        setResults(r)
      } finally {
        setLoading(false)
      }
    }, 300)
  }, [])

  function handleSelect(result: SearchResult) {
    setOpen(false)
    router.push(result.href)
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[10vh]">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40"
        onClick={() => setOpen(false)}
      />

      {/* Modal */}
      <div className="relative w-full max-w-xl mx-4 bg-white rounded-xl shadow-2xl border border-border overflow-hidden">
        {/* Search input */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-border">
          <Search className="h-4 w-4 text-muted-foreground flex-shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={e => handleSearch(e.target.value)}
            placeholder="Search inventory, employees, contacts, leads…"
            className="flex-1 text-sm bg-transparent outline-none placeholder:text-muted-foreground"
          />
          {query && (
            <button onClick={() => handleSearch("")} className="text-muted-foreground hover:text-foreground">
              <X className="h-4 w-4" />
            </button>
          )}
          <kbd className="hidden sm:inline-flex items-center px-1.5 py-0.5 rounded border border-border text-[10px] text-muted-foreground font-mono">
            ESC
          </kbd>
        </div>

        {/* Results */}
        <div className="max-h-[60vh] overflow-y-auto">
          {loading && (
            <div className="px-4 py-6 text-center text-sm text-muted-foreground">Searching…</div>
          )}

          {!loading && query && results.length === 0 && (
            <div className="px-4 py-6 text-center text-sm text-muted-foreground">
              No results for &quot;{query}&quot;
            </div>
          )}

          {!loading && results.length > 0 && (
            <ul className="py-2">
              {results.map(result => (
                <li key={result.id}>
                  <button
                    className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-muted text-left transition-colors"
                    onClick={() => handleSelect(result)}
                  >
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold flex-shrink-0 ${categoryColor(result.category)}`}>
                      {categoryIcon(result.category)}
                      {result.category}
                    </span>
                    <span className="text-sm font-medium truncate">{result.title}</span>
                    <span className="text-xs text-muted-foreground truncate ml-auto">{result.subtitle}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}

          {!query && (
            <div className="px-4 py-6 text-center text-sm text-muted-foreground">
              Type to search across inventory, employees, contacts and leads
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center gap-4 px-4 py-2 border-t border-border bg-muted/30">
          <span className="text-[10px] text-muted-foreground">
            <kbd className="font-mono">↑↓</kbd> navigate &nbsp;
            <kbd className="font-mono">↵</kbd> select &nbsp;
            <kbd className="font-mono">ESC</kbd> close
          </span>
          <span className="ml-auto text-[10px] text-muted-foreground">
            <kbd className="font-mono border border-border rounded px-1">⌘K</kbd> to toggle
          </span>
        </div>
      </div>
    </div>
  )
}

// Export a trigger button for use in AppLayout
export function GlobalSearchTrigger() {
  return (
    <button
      onClick={() => {
        const event = new KeyboardEvent("keydown", { key: "k", metaKey: true, bubbles: true })
        window.dispatchEvent(event)
      }}
      className="flex items-center gap-2 px-3 py-1.5 text-sm text-muted-foreground bg-muted hover:bg-muted/80 rounded-lg border border-border transition-colors"
      title="Global search (⌘K)"
    >
      <Search className="h-3.5 w-3.5" />
      <span className="hidden sm:inline">Search…</span>
      <kbd className="hidden sm:inline-flex items-center px-1 rounded border border-border text-[10px] font-mono">⌘K</kbd>
    </button>
  )
}
