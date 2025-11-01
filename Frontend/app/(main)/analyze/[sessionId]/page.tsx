"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { VideoPlayerWithCanvas } from "@/components/video-player-with-canvas"
import { TimelineBar } from "@/components/timeline-bar"
import { MetricsCard } from "@/components/metrics-card"
import { HeatmapOverlay } from "@/components/heatmap-overlay"
import { useAppStore } from "@/lib/store"
import type { SessionMetrics, StepSegment } from "@/types"

// Dummy data for demonstration
const DUMMY_METRICS: SessionMetrics = {
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
  ],
}

const DUMMY_SEGMENTS: StepSegment[] = [
  {
    stepId: "1",
    name: "Setup",
    startFrame: 0,
    endFrame: 30,
    startTime: 0,
    endTime: 1,
    status: "correct",
  },
  {
    stepId: "2",
    name: "Positioning",
    startFrame: 30,
    endFrame: 90,
    startTime: 1,
    endTime: 3,
    status: "correct",
  },
  {
    stepId: "3",
    name: "Movement",
    startFrame: 90,
    endFrame: 240,
    startTime: 3,
    endTime: 8,
    status: "incorrect",
  },
  {
    stepId: "4",
    name: "Completion",
    startFrame: 240,
    endFrame: 310,
    startTime: 8,
    endTime: 10,
    status: "correct",
  },
]

export default function AnalyzePage() {
  const params = useParams()
  const sessionId = params.sessionId as string
  const { currentSession, setCurrentPlaybackTime, isPlaying, setIsPlaying } = useAppStore()

  const [currentTime, setCurrentTime] = useState(0)
  const [videoUrl, setVideoUrl] = useState("")

  useEffect(() => {
    // Create blob URL from selected file if available
    if (currentSession?.videoFile) {
      const url = URL.createObjectURL(currentSession.videoFile)
      setVideoUrl(url)
      return () => URL.revokeObjectURL(url)
    }
  }, [currentSession?.videoFile])

  const handleTimeUpdate = (time: number) => {
    setCurrentTime(time)
    setCurrentPlaybackTime(time)
  }

  const handleSegmentClick = (segment: StepSegment) => {
    setCurrentTime(segment.startTime)
    setCurrentPlaybackTime(segment.startTime)
  }

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-(--color-text) mb-2">Analysis Results</h1>
        <p className="text-(--color-text-secondary)">Session ID: {sessionId}</p>
      </div>

      {/* Video Player */}
      {videoUrl && (
        <section className="space-y-4">
          <h2 className="text-xl font-semibold text-(--color-text)">Video Analysis</h2>
          <VideoPlayerWithCanvas
            videoUrl={videoUrl}
            framePoses={currentSession?.analysisResult?.frames || []}
            currentTime={currentTime}
            isPlaying={isPlaying}
            onTimeUpdate={handleTimeUpdate}
            onPlayPause={setIsPlaying}
            fps={currentSession?.analysisResult?.fps || 30}
          />
        </section>
      )}

      {/* Timeline */}
      <section className="space-y-4">
        <TimelineBar
          segments={DUMMY_SEGMENTS}
          currentTime={currentTime}
          totalDuration={DUMMY_METRICS.totalDuration}
          onSegmentClick={handleSegmentClick}
        />
      </section>

      {/* Metrics */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-(--color-text)">Performance Metrics</h2>
        <MetricsCard metrics={DUMMY_METRICS} />
      </section>

      {/* Heatmap */}
      <section className="space-y-4">
        <HeatmapOverlay jointLoads={DUMMY_METRICS.jointLoads} videoWidth={640} videoHeight={480} />
      </section>

      {/* Deviations Report */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold text-(--color-text)">Detected Deviations</h2>
        <div className="space-y-2">
          {DUMMY_METRICS.estimatedDeviations.map((dev, idx) => (
            <div key={idx} className="p-4 bg-(--color-surface) border border-(--color-border) rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold text-(--color-text)">{dev.jointName}</p>
                  <p className="text-sm text-(--color-text-secondary)">
                    Frame {dev.frameIndex} • {dev.deviationAmount.toFixed(1)}° deviation
                  </p>
                </div>
                <span
                  className={cn(
                    "px-3 py-1 rounded-full text-xs font-semibold",
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
          ))}
        </div>
      </section>
    </div>
  )
}

function cn(...classes: any[]) {
  return classes.filter(Boolean).join(" ")
}
