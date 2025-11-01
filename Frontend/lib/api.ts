// API client for backend communication
import axios from "axios"
import type { VideoAnalysisResult, ComparisonResult, AnalysisSession } from "@/types"

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:3001",
})

export const videoApi = {
  // Upload and process video
  processVideo: async (file: File): Promise<VideoAnalysisResult> => {
    const formData = new FormData()
    formData.append("video", file)

    try {
      const response = await api.post("/api/process-video", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      return response.data
    } catch (error) {
      console.error("Error processing video:", error)
      throw error
    }
  },

  // Compare two analysis sessions
  compareVideos: async (referenceId: string, comparisonId: string): Promise<ComparisonResult> => {
    try {
      const response = await api.post("/api/compare", {
        referenceSessionId: referenceId,
        comparisonSessionId: comparisonId,
      })
      return response.data
    } catch (error) {
      console.error("Error comparing videos:", error)
      throw error
    }
  },

  // Load session by ID
  getSession: async (sessionId: string): Promise<AnalysisSession> => {
    try {
      const response = await api.get(`/api/session/${sessionId}`)
      return response.data
    } catch (error) {
      console.error("Error loading session:", error)
      throw error
    }
  },
}

export default api
