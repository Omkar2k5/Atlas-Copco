"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

const navItems = [
  { href: "/upload", label: "Upload & Analyze", icon: "↑" },
  { href: "/history", label: "History", icon: "⏱" },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="w-64 bg-(--color-surface) border-r border-(--color-border) p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-(--color-primary)">AssemblyFlow</h1>
        <p className="text-sm text-(--color-text-secondary)">Motion Analysis Platform</p>
      </div>

      <nav className="space-y-2">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-3 px-4 py-2 rounded-md transition-colors",
              pathname === item.href
                ? "bg-(--color-primary) text-white"
                : "text-(--color-text) hover:bg-(--color-background)",
            )}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>
    </aside>
  )
}
