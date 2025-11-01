"use client"

import type { SessionMetrics } from "@/types"

interface MetricsCardProps {
  metrics: SessionMetrics
}

export function MetricsCard({ metrics }: MetricsCardProps) {
  const metricItems = [
    {
      label: "Duration",
      value: `${metrics.totalDuration.toFixed(1)}s`,
      color: "bg-blue-50",
    },
    {
      label: "Avg Speed",
      value: `${metrics.averageSpeed.toFixed(2)}x`,
      color: "bg-purple-50",
    },
    {
      label: "Compliance",
      value: `${metrics.complianceScore.toFixed(0)}%`,
      color: "bg-green-50",
    },
    {
      label: "Errors",
      value: metrics.detectedErrors,
      color: "bg-red-50",
    },
  ]

  return (
    <div className="grid grid-cols-4 gap-4">
      {metricItems.map((item, idx) => (
        <div key={idx} className={cn("p-4 rounded-lg border border-(--color-border)", item.color)}>
          <p className="text-sm text-(--color-text-secondary) mb-1">{item.label}</p>
          <p className="text-2xl font-bold text-(--color-text)">{item.value}</p>
        </div>
      ))}
    </div>
  )
}

function cn(...classes: any[]) {
  return classes.filter(Boolean).join(" ")
}
