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
  const [searchQuery, setSearchQuery] = useState('')

  // Fetch data with auto-refresh every 2 seconds for real-time feel
  const { data: downloads = [], error, isLoading } = useSWR('/api/downloads', fetcher, {
    refreshInterval: 2000,
    revalidateOnFocus: true,
  })

  const { data: stats = {}, error: statsError } = useSWR('/api/stats', fetcher, {
    refreshInterval: 2000,
  })

  // Filter function for search
  const filterDownloads = (download) => {
    if (!searchQuery) return true

    const query = searchQuery.toLowerCase()
    const mediaTitle = (download.media_title || '').toLowerCase()
    const filename = (download.name || '').toLowerCase()
    const category = (download.category || '').toLowerCase()
    const seasonEpisode = download.season && download.episode
      ? `s${String(download.season).padStart(2, '0')}e${String(download.episode).padStart(2, '0')}`
      : ''

    return mediaTitle.includes(query) ||
           filename.includes(query) ||
           category.includes(query) ||
           seasonEpisode.includes(query)
  }

  // Separate downloads by status and apply search filter
  const activeDownload = downloads.find(d => d.status === 'downloading' && !d.failed && filterDownloads(d))

  // CRITICAL: Sort queue by queue_position to match SABnzbd order (#1, #2, #3...)
  const queuedDownloads = downloads
    .filter(d => d.status === 'queued' && !d.failed && filterDownloads(d))
    .sort((a, b) => (a.queue_position || 0) - (b.queue_position || 0))

  const completedDownloads = downloads
    .filter(d => d.status === 'completed' && !d.failed && filterDownloads(d))
    .sort((a, b) => new Date(b.completed_at) - new Date(a.completed_at)) // Newest first (left to right)
  const failedDownloads = downloads.filter(d => d.failed && filterDownloads(d))

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
          <div className="flex items-center justify-between gap-4">
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

            {/* Search Bar */}
            <div className="flex-1 max-w-md hidden lg:block">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search by title, filename, S01E02, category..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full px-4 py-2 pl-10 bg-gray-900/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
                />
                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">
                  🔍
                </div>
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors"
                  >
                    ✕
                  </button>
                )}
              </div>
            </div>

            {/* Failed Toggle */}
            <button
              onClick={() => setShowFailed(!showFailed)}
              className={`px-4 py-2 rounded-lg font-medium transition-all flex-shrink-0 ${
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

          {/* Mobile Search */}
          <div className="mt-3 lg:hidden">
            <div className="relative">
              <input
                type="text"
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 pl-10 bg-gray-900/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
              />
              <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">
                🔍
              </div>
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors"
                >
                  ✕
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6 space-y-8">
        {/* Search Results Indicator */}
        {searchQuery && (
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🔍</span>
              <div>
                <p className="text-blue-400 font-bold">
                  Search Results for "{searchQuery}"
                </p>
                <p className="text-sm text-gray-400">
                  Found {queuedDownloads.length + completedDownloads.length + failedDownloads.length + (activeDownload ? 1 : 0)} matching items
                </p>
              </div>
              <button
                onClick={() => setSearchQuery('')}
                className="ml-auto px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 rounded-lg text-blue-400 font-medium transition-all"
              >
                Clear Search
              </button>
            </div>
          </div>
        )}

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
