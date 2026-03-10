"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import {
  LayoutDashboard,
  Settings,
  Users,
  ShoppingCart,
  Briefcase,
  LogOut,
  Menu,
  X,
} from "lucide-react"
import { useState } from "react"
import { cn } from "@/lib/utils"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"

interface SidebarProps {
  activePage: string
  user: string
  onLogout: () => void
}

const navItems = [
  { href: "/dashboard", label: "Dashboard", key: "dashboard", icon: LayoutDashboard },
  { href: "/operations", label: "Operations", key: "operations", icon: ShoppingCart },
  { href: "/crm", label: "CRM", key: "crm", icon: Briefcase },
  { href: "/hr", label: "HR", key: "hr", icon: Users },
  { href: "/settings", label: "Settings", key: "settings", icon: Settings },
]

export default function Sidebar({ activePage, user, onLogout }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false)

  const initials = user
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2) || "U"

  return (
    <>
      {/* Mobile overlay */}
      {!collapsed && (
        <div
          className="fixed inset-0 z-20 bg-black/40 md:hidden"
          onClick={() => setCollapsed(true)}
        />
      )}

      <aside
        className={cn(
          "flex flex-col h-screen bg-white border-r border-border transition-all duration-300 z-30",
          collapsed ? "w-16" : "w-56",
          "fixed md:static"
        )}
      >
        {/* Logo + toggle */}
        <div className="flex items-center justify-between px-3 py-4 min-h-[64px]">
          {!collapsed && (
            <Link
              href="/dashboard"
              className="flex items-center gap-2 font-bold text-lg"
              style={{ color: "#6D28D9" }}
            >
              <span
                className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-sm font-bold flex-shrink-0"
                style={{ backgroundColor: "#6D28D9" }}
              >
                Bz
              </span>
              BzHub
            </Link>
          )}
          {collapsed && (
            <Link href="/dashboard" className="mx-auto">
              <span
                className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-sm font-bold"
                style={{ backgroundColor: "#6D28D9" }}
              >
                Bz
              </span>
            </Link>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 rounded-md text-muted-foreground hover:bg-muted transition-colors flex-shrink-0"
            aria-label="Toggle sidebar"
          >
            {collapsed ? <Menu className="h-4 w-4" /> : <X className="h-4 w-4" />}
          </button>
        </div>

        <Separator />

        {/* Nav items */}
        <nav className="flex-1 px-2 py-3 space-y-1 overflow-y-auto">
          {navItems.map(({ href, label, key, icon: Icon }) => {
            const isActive = activePage === key
            return (
              <Link
                key={key}
                href={href}
                className={cn(
                  "flex items-center gap-3 px-2 py-2 rounded-lg text-sm font-medium transition-colors",
                  isActive
                    ? "bg-violet-50 text-[#6D28D9]"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                )}
                title={collapsed ? label : undefined}
              >
                <Icon
                  className={cn("h-5 w-5 flex-shrink-0", isActive && "text-[#6D28D9]")}
                />
                {!collapsed && <span>{label}</span>}
              </Link>
            )
          })}
        </nav>

        <Separator />

        {/* User + logout */}
        <div className="px-2 py-3">
          <div
            className={cn(
              "flex items-center gap-2 px-2 py-2 rounded-lg",
              collapsed ? "justify-center" : ""
            )}
          >
            <Avatar className="h-8 w-8 flex-shrink-0">
              <AvatarFallback
                className="text-xs font-semibold text-white"
                style={{ backgroundColor: "#6D28D9" }}
              >
                {initials}
              </AvatarFallback>
            </Avatar>
            {!collapsed && (
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{user}</p>
                <p className="text-xs text-muted-foreground">Logged in</p>
              </div>
            )}
          </div>
          <Button
            variant="ghost"
            size={collapsed ? "icon" : "sm"}
            className={cn(
              "w-full mt-1 text-muted-foreground hover:text-destructive hover:bg-destructive/10",
              collapsed ? "justify-center" : "justify-start gap-2"
            )}
            onClick={onLogout}
            title={collapsed ? "Logout" : undefined}
          >
            <LogOut className="h-4 w-4" />
            {!collapsed && <span>Logout</span>}
          </Button>
        </div>
      </aside>
    </>
  )
}
