"use client"

import { useRef, useEffect } from "react"
import type { JointHeatmapData } from "@/types"
import { getJointColor } from "@/lib/utils"

interface HeatmapOverlayProps {
  jointLoads: JointHeatmapData[]
  videoWidth: number
  videoHeight: number
}

export function HeatmapOverlay({ jointLoads, videoWidth, videoHeight }: HeatmapOverlayProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || jointLoads.length === 0) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const maxLoad = Math.max(...jointLoads.map((j) => j.maxLoad))

    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Simple joint position mapping (approximation)
    const jointPositions: Record<string, [number, number]> = {
      left_shoulder: [100, 150],
      right_shoulder: [540, 150],
      left_elbow: [80, 250],
      right_elbow: [560, 250],
      left_wrist: [50, 350],
      right_wrist: [590, 350],
      left_hip: [120, 400],
      right_hip: [520, 400],
      left_knee: [100, 500],
      right_knee: [540, 500],
    }

    jointLoads.forEach((joint) => {
      const pos = jointPositions[joint.jointName]
      if (pos) {
        const [x, y] = pos
        const color = getJointColor(joint.averageLoad, maxLoad)
        ctx.fillStyle = color
        ctx.beginPath()
        ctx.arc(x, y, 20, 0, Math.PI * 2)
        ctx.fill()

        // Draw load percentage
        ctx.fillStyle = "rgba(0, 0, 0, 0.8)"
        ctx.font = "12px sans-serif"
        ctx.textAlign = "center"
        ctx.textBaseline = "middle"
        ctx.fillText(`${((joint.averageLoad / maxLoad) * 100).toFixed(0)}%`, x, y)
      }
    })
  }, [jointLoads])

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-(--color-text)">Joint Load Heatmap</h3>
      <div
        className="relative w-full bg-black rounded-lg overflow-hidden"
        style={{ aspectRatio: `${videoWidth / videoHeight}` }}
      >
        <canvas ref={canvasRef} width={videoWidth} height={videoHeight} className="w-full h-full" />
      </div>
      <div className="flex gap-4 text-xs text-(--color-text-secondary)">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: "rgba(0, 255, 0, 0.6)" }} />
          <span>Low Load</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: "rgba(255, 165, 0, 0.6)" }} />
          <span>Medium Load</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: "rgba(255, 0, 0, 0.6)" }} />
          <span>High Load</span>
        </div>
      </div>
    </div>
  )
}
