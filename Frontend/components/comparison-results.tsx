"use client"

import type { ComparisonResult } from "@/types"

interface ComparisonResultsProps {
  result: ComparisonResult
}

export function ComparisonResults({ result }: ComparisonResultsProps) {
  const metricItems = [
    {
      label: "Similarity Score",
      value: `${result.similarityScore.toFixed(1)}%`,
      color: "bg-blue-50",
    },
    {
      label: "Compliance",
      value: `${result.compliancePercentage.toFixed(0)}%`,
      color: "bg-green-50",
    },
    {
      label: "Time Difference",
      value: `${result.timeDifference.toFixed(2)}s`,
      color: "bg-purple-50",
    },
    {
      label: "Total Deviations",
      value: result.deviations.length,
      color: "bg-orange-50",
    },
  ]

  return (
    <div className="space-y-6">
      {/* Top metrics */}
      <div className="grid grid-cols-4 gap-4">
        {metricItems.map((item, idx) => (
          <div key={idx} className={cn("p-4 rounded-lg border border-(--color-border)", item.color)}>
            <p className="text-sm text-(--color-text-secondary) mb-1">{item.label}</p>
            <p className="text-2xl font-bold text-(--color-text)">{item.value}</p>
          </div>
        ))}
      </div>

      {/* Detailed deviations */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-(--color-text)">Frame-by-Frame Deviations</h3>
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {result.deviations.length === 0 ? (
            <p className="text-sm text-(--color-text-secondary) p-4 text-center">No significant deviations detected</p>
          ) : (
            result.deviations.map((dev, idx) => (
              <div key={idx} className="p-3 bg-(--color-surface) border border-(--color-border) rounded-md">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-(--color-text)">{dev.jointName}</p>
                    <p className="text-xs text-(--color-text-secondary)">Frame {dev.frameIndex}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-(--color-text)">{dev.deviationAmount.toFixed(2)}°</p>
                    <span
                      className={cn(
                        "text-xs font-semibold px-2 py-1 rounded",
                        dev.severity === "high"
                          ? "bg-red-100 text-red-700"
                          : dev.severity === "medium"
                            ? "bg-yellow-100 text-yellow-700"
                            : "bg-green-100 text-green-700",
                      )}
                    >
                      {dev.severity}
                    </span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Additional metrics */}
      <div className="p-6 bg-(--color-surface) border border-(--color-border) rounded-lg">
        <h3 className="font-semibold text-(--color-text) mb-4">Additional Metrics</h3>
        <div className="space-y-3">
          {Object.entries(result.comparisonMetrics).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between p-2 hover:bg-(--color-background) rounded">
              <span className="text-sm text-(--color-text-secondary)">{key}</span>
              <span className="font-semibold text-(--color-text)">
                {typeof value === "number" ? value.toFixed(2) : value}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function cn(...classes: any[]) {
  return classes.filter(Boolean).join(" ")
}
