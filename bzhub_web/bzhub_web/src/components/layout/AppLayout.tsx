"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Sidebar from "./Sidebar"

interface AppLayoutProps {
  children: React.ReactNode
  activePage: string
}

export default function AppLayout({ children, activePage }: AppLayoutProps) {
  const router = useRouter()
  const [user, setUser] = useState("")

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
      <Sidebar activePage={activePage} user={user} onLogout={handleLogout} />
      <main className="flex-1 overflow-y-auto md:ml-0">
        {children}
      </main>
    </div>
  )
}
