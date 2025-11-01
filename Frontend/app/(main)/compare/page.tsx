"use client"

import { useState } from "react"
import { ComparisonSelector } from "@/components/comparison-selector"
import { ComparisonResults } from "@/components/comparison-results"
import { useAppStore } from "@/lib/store"
import { videoApi } from "@/lib/api"
import type { ComparisonResult } from "@/types"

// Dummy comparison result
const DUMMY_COMPARISON: ComparisonResult = {
  referenceSessionId: "1",
  comparisonSessionId: "2",
  similarityScore: 87.5,
  compliancePercentage: 85,
  timeDifference: 1.2,
  deviations: [
    {
      frameIndex: 45,
      jointName: "left_shoulder",
      deviationAmount: 5.2,
      severity: "low",
    },
    {
      frameIndex: 120,
      jointName: "right_elbow",
      deviationAmount: 12.8,
      severity: "high",
    },
    {
      frameIndex: 200,
      jointName: "left_hip",
      deviationAmount: 8.5,
      severity: "medium",
    },
  ],
  comparisonMetrics: {
    "Average Joint Distance": 3.2,
    "Peak Deviation": 12.8,
    "Motion Smoothness Score": 0.92,
    "Timing Accuracy": 0.89,
  },
}

export default function ComparePage() {
  const { sessions } = useAppStore()
  const [referenceSessionId, setReferenceSessionId] = useState<string>()
  const [comparisonSessionId, setComparisonSessionId] = useState<string>()
  const [comparisonResult, setComparisonResult] = useState<ComparisonResult>()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")

  const handleCompare = async () => {
    if (!referenceSessionId || !comparisonSessionId) {
      setError("Please select both videos")
      return
    }

    setIsLoading(true)
    setError("")

    try {
      // Call API to compare videos
      const result = await videoApi.compareVideos(referenceSessionId, comparisonSessionId)
      setComparisonResult(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to compare videos")
      // Use dummy data for demo
      setComparisonResult(DUMMY_COMPARISON)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-(--color-text) mb-2">Compare Videos</h1>
        <p className="text-(--color-text-secondary)">Analyze differences between two motion analysis sessions</p>
      </div>

      {/* Selector */}
      <ComparisonSelector
        sessions={sessions}
        referenceSessionId={referenceSessionId}
        comparisonSessionId={comparisonSessionId}
        onReferenceChange={setReferenceSessionId}
        onComparisonChange={setComparisonSessionId}
        onCompare={handleCompare}
        isLoading={isLoading}
      />

      {/* Error message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Results */}
      {comparisonResult && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-(--color-text)">Comparison Results</h2>
          <ComparisonResults result={comparisonResult} />
        </div>
      )}

      {/* No results message */}
      {!comparisonResult && !isLoading && (
        <div className="text-center py-12 bg-(--color-surface) border border-(--color-border) rounded-lg">
          <p className="text-(--color-text-secondary)">Select two videos and click Compare to view results</p>
        </div>
      )}
    </div>
  )
}
