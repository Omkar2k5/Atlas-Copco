"use client"

import { useEffect, useRef, useState } from "react"
import type { FramePose } from "@/types"
import { drawPoseSkeleton } from "@/lib/utils"

interface VideoPlayerWithCanvasProps {
  videoUrl: string
  framePoses?: FramePose[]
  onTimeUpdate?: (time: number) => void
  onFrameChange?: (frameIndex: number) => void
  currentTime?: number
  isPlaying?: boolean
  onPlayPause?: (playing: boolean) => void
  fps?: number
}

export function VideoPlayerWithCanvas({
  videoUrl,
  framePoses = [],
  onTimeUpdate,
  onFrameChange,
  currentTime = 0,
  isPlaying = false,
  onPlayPause,
  fps = 30,
}: VideoPlayerWithCanvasProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [dimensions, setDimensions] = useState({ width: 640, height: 480 })
  const animationFrameRef = useRef<number>()

  // Draw pose on canvas
  useEffect(() => {
    const canvas = canvasRef.current
    const video = videoRef.current
    if (!canvas || !video) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const currentFrameIndex = Math.floor((currentTime || 0) * fps)
    const framePose = framePoses.find((fp) => fp.frameIndex === currentFrameIndex)

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Draw pose if available
    if (framePose && framePose.keypoints.length > 0) {
      const scaleX = canvas.width / dimensions.width
      const scaleY = canvas.height / dimensions.height
      drawPoseSkeleton(ctx, framePose.keypoints, scaleX, scaleY)
    }
  }, [currentTime, framePoses, fps, dimensions])

  // Handle video metadata
  const handleLoadedMetadata = () => {
    const video = videoRef.current
    if (video) {
      setDimensions({
        width: video.videoWidth,
        height: video.videoHeight,
      })
    }
  }

  // Handle time updates
  const handleTimeUpdate = () => {
    const video = videoRef.current
    if (video) {
      onTimeUpdate?.(video.currentTime)
      const frameIndex = Math.floor(video.currentTime * fps)
      onFrameChange?.(frameIndex)
    }
  }

  // Handle play/pause
  const handlePlayPause = () => {
    const video = videoRef.current
    if (video) {
      if (video.paused) {
        video.play()
        onPlayPause?.(true)
      } else {
        video.pause()
        onPlayPause?.(false)
      }
    }
  }

  // Sync external currentTime with video
  useEffect(() => {
    const video = videoRef.current
    if (video && Math.abs(video.currentTime - (currentTime || 0)) > 0.1) {
      video.currentTime = currentTime || 0
    }
  }, [currentTime])

  return (
    <div className="flex flex-col gap-4">
      <div className="relative w-full bg-black rounded-lg overflow-hidden aspect-video">
        <video
          ref={videoRef}
          src={videoUrl}
          className="w-full h-full object-contain"
          onLoadedMetadata={handleLoadedMetadata}
          onTimeUpdate={handleTimeUpdate}
          crossOrigin="anonymous"
        />
        <canvas
          ref={canvasRef}
          width={dimensions.width}
          height={dimensions.height}
          className="absolute inset-0 w-full h-full"
        />
      </div>

      {/* Video controls */}
      <div className="flex items-center gap-4">
        <button
          onClick={handlePlayPause}
          className="px-4 py-2 bg-(--color-primary) text-white rounded-md hover:opacity-90 transition-opacity"
        >
          {isPlaying ? "Pause" : "Play"}
        </button>
        <input
          type="range"
          min="0"
          max={videoRef.current?.duration || 100}
          value={currentTime || 0}
          onChange={(e) => {
            const time = Number.parseFloat(e.target.value)
            const video = videoRef.current
            if (video) {
              video.currentTime = time
              onTimeUpdate?.(time)
            }
          }}
          className="flex-1"
        />
        <span className="text-sm text-(--color-text-secondary)">{Math.floor(currentTime || 0)}s</span>
      </div>
    </div>
  )
}
