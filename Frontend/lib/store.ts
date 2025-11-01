// Zustand store for state management
import { create } from "zustand"
import type { AnalysisSession } from "@/types"

interface AppStore {
  // Current session
  currentSession: AnalysisSession | null
  setCurrentSession: (session: AnalysisSession) => void
  clearCurrentSession: () => void

  // Session history
  sessions: AnalysisSession[]
  addSession: (session: AnalysisSession) => void
  removeSession: (sessionId: string) => void

  // UI state
  selectedFrameIndex: number
  setSelectedFrameIndex: (index: number) => void

  // Video playback
  isPlaying: boolean
  setIsPlaying: (playing: boolean) => void
  currentPlaybackTime: number
  setCurrentPlaybackTime: (time: number) => void

  // Comparison state
  referenceSessionId: string | null
  setReferenceSessionId: (id: string | null) => void
}

export const useAppStore = create<AppStore>((set) => ({
  currentSession: null,
  setCurrentSession: (session) => set({ currentSession: session }),
  clearCurrentSession: () => set({ currentSession: null }),

  sessions: [],
  addSession: (session) => set((state) => ({ sessions: [session, ...state.sessions] })),
  removeSession: (sessionId) =>
    set((state) => ({
      sessions: state.sessions.filter((s) => s.id !== sessionId),
    })),

  selectedFrameIndex: 0,
  setSelectedFrameIndex: (index) => set({ selectedFrameIndex: index }),

  isPlaying: false,
  setIsPlaying: (playing) => set({ isPlaying: playing }),
  currentPlaybackTime: 0,
  setCurrentPlaybackTime: (time) => set({ currentPlaybackTime: time }),

  referenceSessionId: null,
  setReferenceSessionId: (id) => set({ referenceSessionId: id }),
}))
