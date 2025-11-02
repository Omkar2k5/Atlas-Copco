"use client"

import Link from "next/link"
import { useEffect, useState } from "react"
import { useHealthCheck } from "@/lib/hooks/use-api"

export default function HomePage() {
  const { data: healthData, loading, checkHealth } = useHealthCheck()
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking")

  useEffect(() => {
    const checkBackend = async () => {
      try {
        await checkHealth()
        setBackendStatus("online")
      } catch (error) {
        setBackendStatus("offline")
      }
    }
    checkBackend()
  }, [checkHealth])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-8">
      <div className="max-w-4xl w-full space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold text-gray-900">
            AssemblyFlow
          </h1>
          <p className="text-xl text-gray-600">
            AI-Powered Motion Analysis & Pose Comparison System
          </p>
          
          {/* Backend Status Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white shadow-sm">
            <div className={`w-2 h-2 rounded-full ${
              backendStatus === "online" ? "bg-green-500" : 
              backendStatus === "offline" ? "bg-red-500" : 
              "bg-yellow-500 animate-pulse"
            }`} />
            <span className="text-sm font-medium">
              Backend: {backendStatus === "checking" ? "Checking..." : backendStatus}
            </span>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-6">
          <Link href="/upload" className="group">
            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow cursor-pointer">
              <div className="text-3xl mb-3">📤</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Upload & Analyze</h3>
              <p className="text-sm text-gray-600">
                Upload videos to extract pose keypoints and generate motion embeddings
              </p>
            </div>
          </Link>

          <Link href="/compare" className="group">
            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow cursor-pointer">
              <div className="text-3xl mb-3">⚖️</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Compare Sessions</h3>
              <p className="text-sm text-gray-600">
                Compare two motion sequences using DTW alignment and get actionable insights
              </p>
            </div>
          </Link>

          <Link href="/history" className="group">
            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow cursor-pointer">
              <div className="text-3xl mb-3">📊</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Session History</h3>
              <p className="text-sm text-gray-600">
                View and manage all your analyzed sessions and comparison results
              </p>
            </div>
          </Link>
        </div>

        {/* Technology Stack */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Powered By</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div className="space-y-1">
              <div className="text-2xl">🤖</div>
              <p className="text-xs font-medium text-gray-700">MoveNet</p>
              <p className="text-xs text-gray-500">Pose Detection</p>
            </div>
            <div className="space-y-1">
              <div className="text-2xl">📏</div>
              <p className="text-xs font-medium text-gray-700">DTW</p>
              <p className="text-xs text-gray-500">Sequence Alignment</p>
            </div>
            <div className="space-y-1">
              <div className="text-2xl">⚡</div>
              <p className="text-xs font-medium text-gray-700">FastAPI</p>
              <p className="text-xs text-gray-500">Backend</p>
            </div>
            <div className="space-y-1">
              <div className="text-2xl">⚛️</div>
              <p className="text-xs font-medium text-gray-700">Next.js</p>
              <p className="text-xs text-gray-500">Frontend</p>
            </div>
          </div>
        </div>

        {/* Backend Info */}
        {healthData && backendStatus === "online" && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 className="font-semibold text-green-900 mb-2">✅ Backend Connected</h4>
            <div className="text-xs text-green-700 space-y-1">
              <p>Service: {healthData.service || "AssemblyFlow API"}</p>
              <p>Status: {healthData.status}</p>
              {healthData.embeddings_count !== undefined && (
                <p>Embeddings: {healthData.embeddings_count}</p>
              )}
              {healthData.sessions_count !== undefined && (
                <p>Sessions: {healthData.sessions_count}</p>
              )}
            </div>
          </div>
        )}

        {backendStatus === "offline" && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h4 className="font-semibold text-red-900 mb-2">⚠️ Backend Offline</h4>
            <p className="text-sm text-red-700">
              Please start the backend server: <code className="bg-red-100 px-2 py-1 rounded">python -m uvicorn app.main:app --reload</code>
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
