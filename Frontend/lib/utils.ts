// Utility functions
export const cn = (...classes: (string | undefined | null | false)[]) => {
  return classes.filter(Boolean).join(" ")
}

export const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, "0")}`
}

export const calculateCompliancePercentage = (correctSteps: number, totalSteps: number): number => {
  return totalSteps > 0 ? (correctSteps / totalSteps) * 100 : 0
}

export const getJointColor = (load: number, maxLoad: number): string => {
  const ratio = load / maxLoad
  if (ratio < 0.33) return "rgba(0, 255, 0, 0.6)" // Green
  if (ratio < 0.66) return "rgba(255, 165, 0, 0.6)" // Orange
  return "rgba(255, 0, 0, 0.6)" // Red
}

export const drawPoseSkeleton = (ctx: CanvasRenderingContext2D, keypoints: any[], scaleX: number, scaleY: number) => {
  const connections = [
    [0, 1],
    [1, 2],
    [2, 3],
    [3, 4],
    [0, 5],
    [5, 6],
    [6, 7],
    [7, 8],
    [5, 11],
    [11, 12],
    [11, 13],
    [13, 15],
    [12, 14],
    [14, 16],
  ]

  // Draw connections
  ctx.strokeStyle = "rgba(0, 255, 0, 0.7)"
  ctx.lineWidth = 2
  connections.forEach(([start, end]) => {
    const startKp = keypoints[start]
    const endKp = keypoints[end]
    if (startKp && endKp && startKp.confidence > 0.5 && endKp.confidence > 0.5) {
      ctx.beginPath()
      ctx.moveTo(startKp.x * scaleX, startKp.y * scaleY)
      ctx.lineTo(endKp.x * scaleX, endKp.y * scaleY)
      ctx.stroke()
    }
  })

  // Draw keypoints
  keypoints.forEach((kp: any) => {
    if (kp.confidence > 0.5) {
      ctx.fillStyle = "rgba(0, 255, 0, 0.8)"
      ctx.beginPath()
      ctx.arc(kp.x * scaleX, kp.y * scaleY, 4, 0, Math.PI * 2)
      ctx.fill()
    }
  })
}
