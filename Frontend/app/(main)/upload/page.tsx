"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { UploadBox } from "@/components/upload-box"
import { useAppStore } from "@/lib/store"
import { videoApi } from "@/lib/api"

export default function UploadPage() {
  const router = useRouter()
  const { setCurrentSession, addSession } = useAppStore()
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [videoPreviewUrl, setVideoPreviewUrl] = useState<string>("")
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState("")

  const handleFileSelect = (file: File) => {
    setSelectedFile(file)
    setError("")

    // Create preview URL
    const url = URL.createObjectURL(file)
    setVideoPreviewUrl(url)
  }

  const handleSubmit = async () => {
    if (!selectedFile) {
      setError("Please select a video file")
      return
    }

    setIsProcessing(true)
    setError("")

    try {
      // Call API to process video
      const result = await videoApi.processVideo(selectedFile)

      // Create session
      const sessionId = crypto.randomUUID()
      const session = {
        id: sessionId,
        videoFile: selectedFile,
        analysisResult: result,
        status: "complete" as const,
      }

      addSession(session as any)
      setCurrentSession(session as any)

      // Redirect to analyze page
      router.push(`/analyze/${sessionId}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to process video")
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-(--color-text) mb-2">Upload & Analyze</h1>
        <p className="text-(--color-text-secondary)">Upload a video to analyze poses and movement patterns</p>
      </div>

      <div className="grid grid-cols-2 gap-8">
        <div className="space-y-4">
          <UploadBox onFileSelect={handleFileSelect} isLoading={isProcessing} />

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          <button
            onClick={handleSubmit}
            disabled={!selectedFile || isProcessing}
            className="w-full px-6 py-3 bg-(--color-primary) text-white font-semibold rounded-lg hover:opacity-90 disabled:opacity-50 transition-opacity"
          >
            {isProcessing ? "Processing..." : "Analyze Video"}
          </button>
        </div>

        {videoPreviewUrl && (
          <div className="space-y-4">
            <h3 className="font-semibold text-(--color-text)">Preview</h3>
            <video src={videoPreviewUrl} controls className="w-full rounded-lg bg-black" />
            <div className="text-sm text-(--color-text-secondary)">
              <p>
                <strong>File:</strong> {selectedFile?.name}
              </p>
              <p>
                <strong>Size:</strong> {((selectedFile?.size || 0) / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
