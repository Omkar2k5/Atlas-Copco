"use client"

import Link from "next/link"
import { useAppStore } from "@/lib/store"

export default function HistoryPage() {
  const { sessions, removeSession } = useAppStore()

  if (sessions.length === 0) {
    return (
      <div className="p-8">
        <h1 className="text-3xl font-bold text-(--color-text) mb-8">Session History</h1>
        <div className="text-center py-12 bg-(--color-surface) border border-(--color-border) rounded-lg">
          <p className="text-(--color-text-secondary)">No analysis sessions yet. Start by uploading a video.</p>
          <Link
            href="/upload"
            className="mt-4 inline-block px-6 py-2 bg-(--color-primary) text-white rounded-lg hover:opacity-90 transition-opacity"
          >
            Upload Video
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-(--color-text) mb-8">Session History</h1>

      <div className="space-y-4">
        {sessions.map((session) => (
          <div
            key={session.id}
            className="p-4 bg-(--color-surface) border border-(--color-border) rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold text-(--color-text)">{session.videoFile.name}</p>
                <p className="text-sm text-(--color-text-secondary)">ID: {session.id}</p>
                <p className="text-sm text-(--color-text-secondary)">Status: {session.status}</p>
              </div>
              <div className="flex gap-2">
                {session.status === "complete" && (
                  <Link
                    href={`/analyze/${session.id}`}
                    className="px-4 py-2 bg-(--color-primary) text-white rounded-lg hover:opacity-90 transition-opacity"
                  >
                    View Results
                  </Link>
                )}
                <button
                  onClick={() => removeSession(session.id)}
                  className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
