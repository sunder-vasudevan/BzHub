"use client"

import { useEffect, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Menu, Bell } from "lucide-react"
import Sidebar from "./Sidebar"
import GlobalSearch, { GlobalSearchTrigger } from "@/components/GlobalSearch"
import { fetchNotifications } from "@/lib/notifications"
import type { AppNotification } from "@/lib/notifications"

interface AppLayoutProps {
  children: React.ReactNode
  activePage: string
}

function severityColor(severity: AppNotification["severity"]) {
  switch (severity) {
    case "urgent": return "border-l-red-500"
    case "warning": return "border-l-amber-500"
    case "info": return "border-l-blue-500"
  }
}

function severityDot(severity: AppNotification["severity"]) {
  switch (severity) {
    case "urgent": return "bg-red-500"
    case "warning": return "bg-amber-500"
    case "info": return "bg-blue-500"
  }
}

export default function AppLayout({ children, activePage }: AppLayoutProps) {
  const router = useRouter()
  const [user, setUser] = useState("")
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [notifications, setNotifications] = useState<AppNotification[]>([])
  const [notifOpen, setNotifOpen] = useState(false)
  const notifRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const stored = localStorage.getItem("bzhub_user")
    if (!stored) {
      router.push("/")
      return
    }
    setUser(stored)
    // Fetch notifications on mount
    fetchNotifications()
      .then(setNotifications)
      .catch(() => {})
  }, [router])

  // Close notification dropdown on outside click
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
        setNotifOpen(false)
      }
    }
    if (notifOpen) {
      document.addEventListener("mousedown", handleClickOutside)
    }
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [notifOpen])

  function handleLogout() {
    localStorage.removeItem("bzhub_user")
    localStorage.removeItem("bzhub_role")
    localStorage.removeItem("bzhub_token")
    router.push("/")
  }

  if (!user) return null

  const unreadCount = notifications.length

  return (
    <div className="flex h-screen bg-[#F5F6FA] overflow-hidden">
      <Sidebar
        activePage={activePage}
        user={user}
        onLogout={handleLogout}
        mobileOpen={sidebarOpen}
        onMobileClose={() => setSidebarOpen(false)}
      />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Mobile top bar */}
        <header className="md:hidden flex items-center justify-between px-4 py-3 bg-white border-b border-border flex-shrink-0">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-1.5 rounded-md text-muted-foreground hover:bg-muted transition-colors"
            aria-label="Open menu"
          >
            <Menu className="h-5 w-5" />
          </button>
          <Link href="/dashboard" className="flex items-center gap-1.5 font-bold text-base" style={{ color: "#6D28D9" }}>
            <span className="w-7 h-7 rounded-lg flex items-center justify-center text-white text-xs font-bold" style={{ backgroundColor: "#6D28D9" }}>
              Bz
            </span>
            BzHub
          </Link>
          {/* Mobile bell */}
          <div className="relative" ref={undefined}>
            <button
              onClick={() => setNotifOpen(!notifOpen)}
              className="relative p-1.5 rounded-md text-muted-foreground hover:bg-muted transition-colors"
              aria-label="Notifications"
            >
              <Bell className="h-5 w-5" />
              {unreadCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full bg-red-500 text-white text-[9px] flex items-center justify-center font-bold">
                  {unreadCount > 9 ? "9+" : unreadCount}
                </span>
              )}
            </button>
          </div>
        </header>

        {/* Desktop top bar */}
        <div className="hidden md:flex items-center justify-end gap-3 px-6 py-2 bg-white border-b border-border flex-shrink-0">
          <GlobalSearchTrigger />

          {/* Bell + dropdown */}
          <div className="relative" ref={notifRef}>
            <button
              onClick={() => setNotifOpen(!notifOpen)}
              className="relative p-1.5 rounded-md text-muted-foreground hover:bg-muted transition-colors"
              aria-label="Notifications"
            >
              <Bell className="h-5 w-5" />
              {unreadCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full bg-red-500 text-white text-[9px] flex items-center justify-center font-bold">
                  {unreadCount > 9 ? "9+" : unreadCount}
                </span>
              )}
            </button>

            {notifOpen && (
              <div className="absolute right-0 top-full mt-2 w-80 bg-white border border-border rounded-xl shadow-xl z-50 overflow-hidden">
                <div className="px-4 py-3 border-b border-border flex items-center justify-between">
                  <p className="text-sm font-semibold">Notifications</p>
                  {unreadCount > 0 && (
                    <span className="text-xs text-muted-foreground">{unreadCount} unread</span>
                  )}
                </div>
                <div className="max-h-80 overflow-y-auto">
                  {notifications.length === 0 ? (
                    <div className="px-4 py-8 text-center text-sm text-muted-foreground">
                      All caught up — no notifications right now
                    </div>
                  ) : (
                    <ul>
                      {notifications.map(notif => (
                        <li key={notif.id}>
                          <Link
                            href={notif.href}
                            onClick={() => setNotifOpen(false)}
                            className={`flex items-start gap-3 px-4 py-3 hover:bg-muted transition-colors border-l-2 ${severityColor(notif.severity)}`}
                          >
                            <span className={`h-2 w-2 rounded-full mt-1.5 flex-shrink-0 ${severityDot(notif.severity)}`} />
                            <div className="min-w-0">
                              <p className="text-sm font-medium leading-snug">{notif.title}</p>
                              <p className="text-xs text-muted-foreground mt-0.5 leading-snug">{notif.body}</p>
                            </div>
                          </Link>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>

      {/* Global Search modal — rendered at root level */}
      <GlobalSearch />
    </div>
  )
}
