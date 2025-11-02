/**
 * Custom React hooks for AssemblyFlow API
 * Provides state management and easy integration with the backend
 */

import { useState, useCallback } from 'react';
import { 
  api, 
  getErrorMessage,
  ProcessVideoResponse,
  CompareResponse,
  SessionResponse,
  SessionListResponse,
  DTWPreset 
} from '../api-client';

// Generic API hook state
interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  progress?: number;
}

// ============ Video Processing Hook ============

export function useProcessVideo() {
  const [state, setState] = useState<UseApiState<ProcessVideoResponse>>({
    data: null,
    loading: false,
    error: null,
    progress: 0,
  });

  const processVideo = useCallback(async (videoFile: File) => {
    setState({ data: null, loading: true, error: null, progress: 0 });

    try {
      const result = await api.processVideo(videoFile, (progress) => {
        setState((prev) => ({ ...prev, progress }));
      });

      setState({ data: result, loading: false, error: null, progress: 100 });
      return result;
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      setState({ data: null, loading: false, error: errorMessage, progress: 0 });
      throw error;
    }
  }, []);

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null, progress: 0 });
  }, []);

  return {
    ...state,
    processVideo,
    reset,
  };
}

// ============ Session Comparison Hook ============

export function useCompare() {
  const [state, setState] = useState<UseApiState<CompareResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  const compare = useCallback(
    async (
      referenceId: string,
      userId: string,
      preset?: DTWPreset
    ) => {
      setState({ data: null, loading: true, error: null });

      try {
        const result = await api.compare(referenceId, userId, preset);
        setState({ data: result, loading: false, error: null });
        return result;
      } catch (error) {
        const errorMessage = getErrorMessage(error);
        setState({ data: null, loading: false, error: errorMessage });
        throw error;
      }
    },
    []
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return {
    ...state,
    compare,
    reset,
  };
}

// ============ Session Management Hook ============

export function useSession() {
  const [sessionState, setSessionState] = useState<UseApiState<SessionResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  const getSession = useCallback(async (sessionId: string) => {
    setSessionState({ data: null, loading: true, error: null });

    try {
      const result = await api.getSession(sessionId);
      setSessionState({ data: result, loading: false, error: null });
      return result;
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      setSessionState({ data: null, loading: false, error: errorMessage });
      throw error;
    }
  }, []);

  const reset = useCallback(() => {
    setSessionState({ data: null, loading: false, error: null });
  }, []);

  return {
    session: sessionState.data,
    loading: sessionState.loading,
    error: sessionState.error,
    getSession,
    reset,
  };
}

// ============ Session List Hook ============

export function useSessions() {
  const [state, setState] = useState<UseApiState<SessionListResponse>>({
    data: null,
    loading: false,
    error: null,
  });

  const fetchSessions = useCallback(async (userId?: string) => {
    setState({ data: null, loading: true, error: null });

    try {
      const result = await api.listSessions(userId);
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      setState({ data: null, loading: false, error: errorMessage });
      throw error;
    }
  }, []);

  const deleteSession = useCallback(
    async (sessionId: string) => {
      try {
        await api.deleteSession(sessionId);
        // Refetch sessions after deletion
        if (state.data) {
          const updatedSessions = state.data.sessions.filter(
            (s) => s.session_id !== sessionId
          );
          setState((prev) => ({
            ...prev,
            data: prev.data ? { sessions: updatedSessions } : null,
          }));
        }
      } catch (error) {
        const errorMessage = getErrorMessage(error);
        setState((prev) => ({ ...prev, error: errorMessage }));
        throw error;
      }
    },
    [state.data]
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return {
    sessions: state.data?.sessions || [],
    loading: state.loading,
    error: state.error,
    fetchSessions,
    deleteSession,
    reset,
  };
}

// ============ Health Check Hook ============

export function useHealthCheck() {
  const [state, setState] = useState<UseApiState<any>>({
    data: null,
    loading: false,
    error: null,
  });

  const checkHealth = useCallback(async () => {
    setState({ data: null, loading: true, error: null });

    try {
      const result = await api.health();
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      setState({ data: null, loading: false, error: errorMessage });
      throw error;
    }
  }, []);

  return {
    ...state,
    checkHealth,
  };
}
