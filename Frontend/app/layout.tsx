import type React from "react"
import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "AssemblyFlow - Motion Analysis",
  description: "Analyze and compare human pose movements",
    generator: 'v0.app'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-(--color-background)">{children}</body>
    </html>
  )
}
