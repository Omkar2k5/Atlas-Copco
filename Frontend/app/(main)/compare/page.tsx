"use client"

import { useState } from "react"
import { ComparisonSelector } from "@/components/comparison-selector"
import { ComparisonResults } from "@/components/comparison-results"
import { useAppStore } from "@/lib/store"
import { useCompare } from "@/lib/hooks/use-api"
import type { ComparisonResult } from "@/types"
import type { DTWPreset } from "@/lib/api-client"

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
  const { data: compareData, loading, error: apiError, compare, reset } = useCompare()
  const [referenceSessionId, setReferenceSessionId] = useState<string>()
  const [comparisonSessionId, setComparisonSessionId] = useState<string>()
  const [comparisonResult, setComparisonResult] = useState<ComparisonResult>()
  const [preset, setPreset] = useState<DTWPreset>("balanced")
  const [error, setError] = useState("")

  const handleCompare = async () => {
    if (!referenceSessionId || !comparisonSessionId) {
      setError("Please select both videos")
      return
    }

    setError("")
    reset()

    try {
      // Call backend API to compare sessions using DTW
      const result = await compare(referenceSessionId, comparisonSessionId, preset)

      // Transform backend response to frontend format
      const transformedResult: ComparisonResult = {
        referenceSessionId,
        comparisonSessionId,
        similarityScore: result.similarity_score,
        compliancePercentage: result.similarity_percentage || result.similarity_score * 100,
        timeDifference: result.time_difference_seconds,
        deviations: [], // Can be computed from movement_deviation_vector if needed
        comparisonMetrics: {
          "DTW Similarity Score": result.similarity_score,
          "Time Difference (s)": result.time_difference_seconds,
          "Stressed Joints": result.stressed_joints.length,
          "Method": result.method || "DTW",
        },
        stressedJoints: result.stressed_joints,
        recommendations: result.recommended_improvements,
      }

      setComparisonResult(transformedResult)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to compare videos")
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
      <div className="space-y-4">
        <ComparisonSelector
          sessions={sessions}
          referenceSessionId={referenceSessionId}
          comparisonSessionId={comparisonSessionId}
          onReferenceChange={setReferenceSessionId}
          onComparisonChange={setComparisonSessionId}
          onCompare={handleCompare}
          isLoading={loading}
        />

        {/* DTW Preset Selector */}
        <div className="flex items-center gap-4 p-4 bg-(--color-surface) border border-(--color-border) rounded-lg">
          <label className="text-sm font-medium text-(--color-text)">DTW Preset:</label>
          <select
            value={preset}
            onChange={(e) => setPreset(e.target.value as DTWPreset)}
            className="px-3 py-2 border border-(--color-border) rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-(--color-primary)"
            disabled={loading}
          >
            <option value="balanced">Balanced (Default)</option>
            <option value="precise">Precise (Slower, More Accurate)</option>
            <option value="fast">Fast (Quick Comparison)</option>
            <option value="long_sequences">Long Sequences (Optimized for Long Videos)</option>
          </select>
          <span className="text-xs text-(--color-text-secondary)">
            {preset === "balanced" && "Good balance between speed and accuracy"}
            {preset === "precise" && "Higher accuracy with more computation"}
            {preset === "fast" && "Quick results with lower precision"}
            {preset === "long_sequences" && "Optimized for videos longer than 30s"}
          </span>
        </div>
      </div>

      {/* Error message */}
      {(error || apiError) && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{error || apiError}</p>
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
      {!comparisonResult && !loading && (
        <div className="text-center py-12 bg-(--color-surface) border border-(--color-border) rounded-lg">
          <p className="text-(--color-text-secondary)">Select two videos and click Compare to view results</p>
        </div>
      )}
    </div>
  )
}
