"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Menu } from "lucide-react"
import Sidebar from "./Sidebar"

interface AppLayoutProps {
  children: React.ReactNode
  activePage: string
}

export default function AppLayout({ children, activePage }: AppLayoutProps) {
  const router = useRouter()
  const [user, setUser] = useState("")
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem("bzhub_user")
    if (!stored) {
      router.push("/")
      return
    }
    setUser(stored)
  }, [router])

  function handleLogout() {
    localStorage.removeItem("bzhub_user")
    localStorage.removeItem("bzhub_role")
    localStorage.removeItem("bzhub_token")
    router.push("/")
  }

  if (!user) return null

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
          <div className="w-8" />
        </header>
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
