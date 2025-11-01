"use client"

import { useParams } from "next/navigation"
import { useAppStore } from "@/lib/store"
import { MetricsCard } from "@/components/metrics-card"
import { HeatmapOverlay } from "@/components/heatmap-overlay"
import type { SessionMetrics } from "@/types"

// Dummy report data
const DUMMY_REPORT: SessionMetrics = {
  totalDuration: 15.5,
  averageSpeed: 1.2,
  complianceScore: 92,
  detectedErrors: 2,
  estimatedDeviations: [
    {
      frameIndex: 45,
      jointName: "left_shoulder",
      deviationAmount: 5.2,
      severity: "medium",
    },
    {
      frameIndex: 120,
      jointName: "right_elbow",
      deviationAmount: 8.1,
      severity: "high",
    },
  ],
  jointLoads: [
    { jointName: "left_shoulder", averageLoad: 42, maxLoad: 85, occurrences: 23 },
    { jointName: "right_shoulder", averageLoad: 38, maxLoad: 85, occurrences: 23 },
    { jointName: "left_elbow", averageLoad: 55, maxLoad: 85, occurrences: 23 },
    { jointName: "right_elbow", averageLoad: 62, maxLoad: 85, occurrences: 23 },
    { jointName: "left_hip", averageLoad: 48, maxLoad: 85, occurrences: 23 },
    { jointName: "right_hip", averageLoad: 45, maxLoad: 85, occurrences: 23 },
  ],
}

const SUGGESTED_IMPROVEMENTS = [
  {
    title: "Shoulder Positioning",
    description: "Right shoulder shows elevated stress. Consider adjusting posture to keep shoulders more relaxed.",
    priority: "high",
  },
  {
    title: "Elbow Angle",
    description: "Maintain a consistent 90-degree elbow angle throughout the movement for optimal efficiency.",
    priority: "medium",
  },
  {
    title: "Movement Timing",
    description: "Frame 120 shows a deviation spike. Practice smoother transitions between steps.",
    priority: "high",
  },
  {
    title: "Hip Stability",
    description: "Minor hip fluctuations detected. Engage core muscles for better stability.",
    priority: "low",
  },
]

export default function ReportPage() {
  const params = useParams()
  const sessionId = params.sessionId as string
  const { sessions } = useAppStore()

  const session = sessions.find((s) => s.id === sessionId)
  const metrics = session?.metrics || DUMMY_REPORT

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-(--color-text) mb-2">Analysis Report</h1>
        <p className="text-(--color-text-secondary)">Session ID: {sessionId}</p>
      </div>

      {/* Key Metrics */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-(--color-text)">Key Metrics</h2>
        <MetricsCard metrics={metrics} />
      </section>

      {/* Summary Statistics */}
      <section className="grid grid-cols-2 gap-4">
        <div className="p-6 bg-(--color-surface) border border-(--color-border) rounded-lg">
          <h3 className="text-lg font-semibold text-(--color-text) mb-4">Summary</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-(--color-text-secondary)">Total Duration</span>
              <span className="font-semibold text-(--color-text)">{metrics.totalDuration.toFixed(1)}s</span>
            </div>
            <div className="flex justify-between">
              <span className="text-(--color-text-secondary)">Average Speed</span>
              <span className="font-semibold text-(--color-text)">{metrics.averageSpeed.toFixed(2)}x</span>
            </div>
            <div className="flex justify-between">
              <span className="text-(--color-text-secondary)">Compliance Score</span>
              <span className="font-semibold text-(--color-text)">{metrics.complianceScore.toFixed(0)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-(--color-text-secondary)">Errors Detected</span>
              <span className="font-semibold text-(--color-text)">{metrics.detectedErrors}</span>
            </div>
          </div>
        </div>

        {/* Deviation Summary */}
        <div className="p-6 bg-(--color-surface) border border-(--color-border) rounded-lg">
          <h3 className="text-lg font-semibold text-(--color-text) mb-4">Deviation Breakdown</h3>
          <div className="space-y-2">
            {metrics.estimatedDeviations.map((dev, idx) => (
              <div key={idx} className="flex justify-between items-center">
                <span className="text-sm text-(--color-text)">{dev.jointName}</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 bg-(--color-background) rounded-full h-2">
                    <div
                      className={cn(
                        "h-full rounded-full transition-all",
                        dev.severity === "high"
                          ? "bg-red-500"
                          : dev.severity === "medium"
                            ? "bg-yellow-500"
                            : "bg-green-500",
                      )}
                      style={{
                        width: `${(dev.deviationAmount / 15) * 100}%`,
                      }}
                    />
                  </div>
                  <span className="text-xs font-semibold text-(--color-text-secondary) w-8">
                    {dev.deviationAmount.toFixed(1)}°
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Heatmap */}
      <section className="space-y-4">
        <HeatmapOverlay jointLoads={metrics.jointLoads} videoWidth={640} videoHeight={480} />
      </section>

      {/* Suggested Improvements */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-(--color-text)">Suggested Improvements</h2>
        <div className="space-y-3">
          {SUGGESTED_IMPROVEMENTS.map((improvement, idx) => (
            <div key={idx} className="p-4 bg-(--color-surface) border border-(--color-border) rounded-lg">
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-semibold text-(--color-text)">{improvement.title}</h4>
                <span
                  className={cn(
                    "px-3 py-1 rounded-full text-xs font-semibold",
                    improvement.priority === "high"
                      ? "bg-red-100 text-red-700"
                      : improvement.priority === "medium"
                        ? "bg-yellow-100 text-yellow-700"
                        : "bg-blue-100 text-blue-700",
                  )}
                >
                  {improvement.priority}
                </span>
              </div>
              <p className="text-sm text-(--color-text-secondary)">{improvement.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Export Options */}
      <section className="flex gap-4">
        <button className="px-6 py-3 bg-(--color-primary) text-white font-semibold rounded-lg hover:opacity-90 transition-opacity">
          Export Report (PDF)
        </button>
        <button className="px-6 py-3 bg-(--color-secondary) text-white font-semibold rounded-lg hover:opacity-90 transition-opacity">
          Export Data (CSV)
        </button>
      </section>
    </div>
  )
}

function cn(...classes: any[]) {
  return classes.filter(Boolean).join(" ")
}
