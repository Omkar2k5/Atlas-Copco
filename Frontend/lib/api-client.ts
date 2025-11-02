/**
 * AssemblyFlow Backend API Client
 * Handles all communication with the FastAPI backend
 */

import axios, { AxiosInstance } from 'axios';

// Backend configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 900000, // 15 minutes for video processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface ProcessVideoResponse {
  session_id: string;
  keypoints: number[][][]; // [frame][joint][x, y, confidence]
  embedding: number[];
  step_segments: null | any; // Placeholder
  duration_seconds: number;
}

export interface CompareRequest {
  session_id_reference: string;
  session_id_user: string;
}

export interface CompareResponse {
  similarity_score: number;
  similarity_percentage?: number;
  time_difference_seconds: number;
  movement_deviation_vector: number[];
  stressed_joints: string[];
  recommended_improvements: string[];
  method?: string; // DTW method used
}

export interface SessionResponse {
  session_id: string;
  timestamp: string;
  user_id: string | null;
  video_path: string | null;
  duration_seconds: number;
  keypoints: number[][][];
  embedding: number[];
  step_segments: null | any;
}

export interface SessionListResponse {
  sessions: Array<{
    session_id: string;
    timestamp: string;
    user_id: string | null;
    duration_seconds: number;
  }>;
}

export type DTWPreset = 'precise' | 'balanced' | 'fast' | 'long_sequences';

// API Methods
export const api = {
  /**
   * Health check
   */
  async health() {
    const response = await apiClient.get('/health');
    return response.data;
  },

  /**
   * Upload and process video
   * @param videoFile - Video file to process
   * @param onProgress - Optional progress callback
   */
  async processVideo(
    videoFile: File,
    onProgress?: (progress: number) => void
  ): Promise<ProcessVideoResponse> {
    const formData = new FormData();
    formData.append('video', videoFile);

    const response = await apiClient.post<ProcessVideoResponse>(
      '/api/process-video',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            onProgress(progress);
          }
        },
      }
    );

    return response.data;
  },

  /**
   * Compare two sessions using DTW
   * @param referenceId - Reference session ID
   * @param userId - User session ID to compare
   * @param preset - Optional DTW preset (precise, balanced, fast, long_sequences)
   */
  async compare(
    referenceId: string,
    userId: string,
    preset?: DTWPreset
  ): Promise<CompareResponse> {
    const params = preset ? { preset } : {};

    const response = await apiClient.post<CompareResponse>(
      '/api/compare',
      {
        session_id_reference: referenceId,
        session_id_user: userId,
      },
      { params }
    );

    return response.data;
  },

  /**
   * Get session by ID
   * @param sessionId - Session ID to retrieve
   */
  async getSession(sessionId: string): Promise<SessionResponse> {
    const response = await apiClient.get<SessionResponse>(
      `/api/session/${sessionId}`
    );
    return response.data;
  },

  /**
   * List all sessions
   * @param userId - Optional user ID filter
   */
  async listSessions(userId?: string): Promise<SessionListResponse> {
    const params = userId ? { user_id: userId } : {};
    const response = await apiClient.get<SessionListResponse>(
      '/api/sessions',
      { params }
    );
    return response.data;
  },

  /**
   * Delete session
   * @param sessionId - Session ID to delete
   */
  async deleteSession(sessionId: string): Promise<{ message: string }> {
    const response = await apiClient.delete(`/api/session/${sessionId}`);
    return response.data;
  },
};

// Error handling helper
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    return error.response?.data?.detail || error.message || 'An error occurred';
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unknown error occurred';
}

export default apiClient;
