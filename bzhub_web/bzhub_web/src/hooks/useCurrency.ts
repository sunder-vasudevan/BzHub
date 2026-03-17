"use client"
import { useEffect, useState } from "react"

export function useCurrency() {
  const [symbol, setSymbol] = useState("₹")
  useEffect(() => {
    const load = () => {
      const stored = localStorage.getItem("bzhub_currency")
      if (stored) setSymbol(stored)
    }
    load()
    window.addEventListener("bzhub_currency_changed", load)
    return () => window.removeEventListener("bzhub_currency_changed", load)
  }, [])
  return symbol
}
