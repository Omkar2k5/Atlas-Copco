// TypeScript interfaces for AssemblyFlow data structures

export interface PoseKeypoint {
  name: string
  x: number
  y: number
  confidence: number
}

export interface FramePose {
  frameIndex: number
  timestamp: number
  keypoints: PoseKeypoint[]
}

export interface StepSegment {
  stepId: string
  name: string
  startFrame: number
  endFrame: number
  startTime: number
  endTime: number
  status: "correct" | "incorrect" | "pending"
}

export interface VideoAnalysisResult {
  sessionId: string
  videoUrl: string
  duration: number
  fps: number
  frames: FramePose[]
  embedding: number[]
  stepSegments: StepSegment[]
  createdAt: string
}

export interface ComparisonResult {
  referenceSessionId: string
  comparisonSessionId: string
  similarityScore: number
  compliancePercentage: number
  timeDifference: number
  deviations: Deviation[]
  comparisonMetrics: Record<string, number>
}

export interface Deviation {
  frameIndex: number
  jointName: string
  deviationAmount: number
  severity: "low" | "medium" | "high"
}

export interface JointHeatmapData {
  jointName: string
  averageLoad: number
  maxLoad: number
  occurrences: number
}

export interface SessionMetrics {
  totalDuration: number
  averageSpeed: number
  complianceScore: number
  detectedErrors: number
  estimatedDeviations: Deviation[]
  jointLoads: JointHeatmapData[]
}

export interface AnalysisSession {
  id: string
  videoFile: File
  analysisResult?: VideoAnalysisResult
  metrics?: SessionMetrics
  comparisonResult?: ComparisonResult
  status: "uploading" | "analyzing" | "complete" | "error"
  errorMessage?: string
}
