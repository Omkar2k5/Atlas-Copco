"use client"

import type { StepSegment } from "@/types"
import { cn } from "@/lib/utils"

interface TimelineBarProps {
  segments: StepSegment[]
  currentTime: number
  totalDuration: number
  onSegmentClick?: (segment: StepSegment) => void
  height?: string
}

export function TimelineBar({
  segments,
  currentTime,
  totalDuration,
  onSegmentClick,
  height = "h-16",
}: TimelineBarProps) {
  const progressPercent = (currentTime / totalDuration) * 100

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-(--color-text)">Step Timeline</h3>
      <div className={cn("relative w-full bg-(--color-background) rounded-md overflow-hidden", height)}>
        {/* Segments */}
        {segments.map((segment, idx) => {
          const startPercent = (segment.startTime / totalDuration) * 100
          const widthPercent = ((segment.endTime - segment.startTime) / totalDuration) * 100

          const bgColor =
            segment.status === "correct"
              ? "bg-green-500"
              : segment.status === "incorrect"
                ? "bg-red-500"
                : "bg-gray-400"

          return (
            <button
              key={idx}
              onClick={() => onSegmentClick?.(segment)}
              className={cn(
                "absolute top-0 bottom-0 border-r border-(--color-border) hover:opacity-80 transition-opacity",
                bgColor,
              )}
              style={{
                left: `${startPercent}%`,
                width: `${widthPercent}%`,
              }}
              title={`${segment.name} (${segment.status})`}
            >
              <div className="p-1 text-xs text-white font-bold truncate">{segment.name}</div>
            </button>
          )
        })}

        {/* Progress indicator */}
        <div
          className="absolute top-0 bottom-0 w-1 bg-(--color-primary) shadow-lg z-10 pointer-events-none"
          style={{ left: `${progressPercent}%` }}
        />
      </div>
    </div>
  )
}
