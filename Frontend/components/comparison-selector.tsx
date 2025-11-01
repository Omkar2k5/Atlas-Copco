"use client"

import type { AnalysisSession } from "@/types"

interface ComparisonSelectorProps {
  sessions: AnalysisSession[]
  referenceSessionId?: string
  comparisonSessionId?: string
  onReferenceChange: (id: string) => void
  onComparisonChange: (id: string) => void
  onCompare: () => void
  isLoading?: boolean
}

export function ComparisonSelector({
  sessions,
  referenceSessionId,
  comparisonSessionId,
  onReferenceChange,
  onComparisonChange,
  onCompare,
  isLoading,
}: ComparisonSelectorProps) {
  const completedSessions = sessions.filter((s) => s.status === "complete")

  return (
    <div className="space-y-4 p-6 bg-(--color-surface) border border-(--color-border) rounded-lg">
      <h3 className="text-lg font-semibold text-(--color-text)">Select Videos to Compare</h3>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-(--color-text) mb-2">Reference Video</label>
          <select
            value={referenceSessionId || ""}
            onChange={(e) => onReferenceChange(e.target.value)}
            className="w-full p-2 border border-(--color-border) rounded-md focus:outline-none focus:ring-2 focus:ring-(--color-primary)"
          >
            <option value="">Select reference video</option>
            {completedSessions.map((session) => (
              <option key={session.id} value={session.id}>
                {session.videoFile.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-(--color-text) mb-2">Comparison Video</label>
          <select
            value={comparisonSessionId || ""}
            onChange={(e) => onComparisonChange(e.target.value)}
            className="w-full p-2 border border-(--color-border) rounded-md focus:outline-none focus:ring-2 focus:ring-(--color-primary)"
          >
            <option value="">Select comparison video</option>
            {completedSessions
              .filter((s) => s.id !== referenceSessionId)
              .map((session) => (
                <option key={session.id} value={session.id}>
                  {session.videoFile.name}
                </option>
              ))}
          </select>
        </div>
      </div>

      <button
        onClick={onCompare}
        disabled={!referenceSessionId || !comparisonSessionId || isLoading}
        className="w-full px-6 py-2 bg-(--color-primary) text-white font-semibold rounded-lg hover:opacity-90 disabled:opacity-50 transition-opacity"
      >
        {isLoading ? "Comparing..." : "Compare Videos"}
      </button>
    </div>
  )
}
