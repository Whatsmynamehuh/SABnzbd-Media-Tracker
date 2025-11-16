import { useState } from 'react'
import useSWR from 'swr'
import axios from 'axios'
import HeroDownload from './components/HeroDownload'
import QueueSection from './components/QueueSection'
import CompletedSection from './components/CompletedSection'
import FailedSection from './components/FailedSection'

const fetcher = (url) => axios.get(url).then(res => res.data)

function App() {
  const [showFailed, setShowFailed] = useState(false)

  // Fetch data with auto-refresh every 2 seconds for real-time feel
  const { data: downloads = [], error, isLoading } = useSWR('/api/downloads', fetcher, {
    refreshInterval: 2000,
    revalidateOnFocus: true,
  })

  const { data: stats = {}, error: statsError } = useSWR('/api/stats', fetcher, {
    refreshInterval: 2000,
  })

  // Separate downloads by status
  const activeDownload = downloads.find(d => d.status === 'downloading' && !d.failed)
  const queuedDownloads = downloads.filter(d => d.status === 'queued' && !d.failed)
  const completedDownloads = downloads
    .filter(d => d.status === 'completed' && !d.failed)
    .sort((a, b) => new Date(b.completed_at) - new Date(a.completed_at)) // Newest first (left to right)
  const failedDownloads = downloads.filter(d => d.failed)

  if (error || statsError) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-jellyseerr-dark">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-500 mb-4">Error Loading Data</h1>
          <p className="text-gray-400">Please check your backend connection and configuration.</p>
          <p className="text-sm text-gray-500 mt-2">Make sure config.yml exists and is properly configured.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-jellyseerr-dark">
      {/* Header */}
      <header className="bg-jellyseerr-card border-b border-gray-800 sticky top-0 z-50 backdrop-blur-sm bg-opacity-95">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            {/* Logo & Stats */}
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <span className="text-2xl">⚡</span>
                <h1 className="text-xl font-bold text-white">SABnzbd</h1>
              </div>

              {/* Inline Stats Pills */}
              <div className="hidden md:flex items-center gap-3 text-sm">
                <div className="px-3 py-1.5 bg-orange-500/20 text-orange-400 rounded-full font-medium border border-orange-500/30">
                  Downloading: {stats.downloading || 0}
                </div>
                <div className="px-3 py-1.5 bg-blue-500/20 text-blue-400 rounded-full font-medium border border-blue-500/30">
                  Queued: {stats.queued || 0}
                </div>
                <div className="px-3 py-1.5 bg-green-500/20 text-green-400 rounded-full font-medium border border-green-500/30">
                  Completed: {stats.completed || 0}
                </div>
              </div>
            </div>

            {/* Failed Toggle */}
            <button
              onClick={() => setShowFailed(!showFailed)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                showFailed
                  ? 'bg-red-500 text-white'
                  : stats.failed > 0
                  ? 'bg-red-500/20 text-red-400 border border-red-500/30 animate-pulse'
                  : 'bg-gray-800 text-gray-400 border border-gray-700'
              }`}
            >
              {showFailed ? '✕ Hide Failed' : `⚠️ Failed (${stats.failed || 0})`}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6 space-y-8">
        {showFailed ? (
          <FailedSection downloads={failedDownloads} />
        ) : (
          <>
            {/* Hero Download */}
            <HeroDownload download={activeDownload} isLoading={isLoading} />

            {/* Queue */}
            <QueueSection downloads={queuedDownloads} />

            {/* Recently Completed */}
            <CompletedSection downloads={completedDownloads} />
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="text-center py-6 text-gray-500 text-sm">
        <div className="flex items-center justify-center gap-2">
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          Live updates every 2s
          <span className="text-gray-700">•</span>
          Auto-cleanup after 48h
        </div>
      </footer>
    </div>
  )
}

export default App
