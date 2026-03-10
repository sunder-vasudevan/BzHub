"use client"
import { useEffect, useState } from "react"

export function useCurrency() {
  const [symbol, setSymbol] = useState("₹")
  useEffect(() => {
    const stored = localStorage.getItem("bzhub_currency")
    if (stored) setSymbol(stored)
  }, [])
  return symbol
}
