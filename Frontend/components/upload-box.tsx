"use client"

import type React from "react"

import { useRef, useState } from "react"

interface UploadBoxProps {
  onFileSelect: (file: File) => void
  isLoading?: boolean
}

export function UploadBox({ onFileSelect, isLoading = false }: UploadBoxProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const handleFile = (file: File) => {
    if (file.type.startsWith("video/")) {
      setSelectedFile(file)
      onFileSelect(file)
    } else {
      alert("Please select a valid video file")
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  return (
    <div
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      className={cn(
        "relative border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer",
        dragActive ? "border-(--color-primary) bg-blue-50" : "border-(--color-border) bg-(--color-background)",
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept="video/*"
        onChange={(e) => {
          if (e.target.files?.[0]) {
            handleFile(e.target.files[0])
          }
        }}
        className="hidden"
        disabled={isLoading}
      />

      <button onClick={() => inputRef.current?.click()} disabled={isLoading} className="w-full">
        <div className="text-4xl mb-4">📹</div>
        <h3 className="text-lg font-semibold text-(--color-text) mb-2">
          {selectedFile ? selectedFile.name : "Upload Video"}
        </h3>
        <p className="text-sm text-(--color-text-secondary)">
          {isLoading ? "Processing video..." : "Drag and drop your video or click to browse"}
        </p>
      </button>
    </div>
  )
}

function cn(...classes: any[]) {
  return classes.filter(Boolean).join(" ")
}
