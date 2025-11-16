import { useState } from 'react'
import useSWR from 'swr'
import axios from 'axios'
import DownloadSection from './components/DownloadSection'
import StatsBar from './components/StatsBar'
import Navigation from './components/Navigation'

const fetcher = (url) => axios.get(url).then(res => res.data)

function App() {
  const [activeSection, setActiveSection] = useState('downloading')
  const [showFailed, setShowFailed] = useState(false)

  // Fetch data with auto-refresh every 5 seconds
  const { data: downloads = [], error, isLoading } = useSWR('/api/downloads', fetcher, {
    refreshInterval: 5000,
    revalidateOnFocus: true,
  })

  const { data: stats = {}, error: statsError } = useSWR('/api/stats', fetcher, {
    refreshInterval: 5000,
  })

  // Filter downloads by section
  const filterDownloads = () => {
    if (showFailed) {
      return downloads.filter(d => d.failed)
    }

    switch (activeSection) {
      case 'downloading':
        return downloads.filter(d => d.status === 'downloading' && !d.failed)
      case 'queued':
        return downloads.filter(d => d.status === 'queued' && !d.failed)
      case 'completed':
        return downloads.filter(d => d.status === 'completed' && !d.failed)
      default:
        return []
    }
  }

  const filteredDownloads = filterDownloads()

  if (error || statsError) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-500 mb-4">Error Loading Data</h1>
          <p className="text-gray-400">Please check your backend connection and configuration.</p>
          <p className="text-sm text-gray-500 mt-2">Make sure config.yml exists and is properly configured.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-orange-500/10 to-transparent rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-purple-500/10 to-transparent rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      {/* Header */}
      <header className="relative backdrop-blur-xl bg-white/5 border-b border-white/10 sticky top-0 z-50 shadow-2xl">
        <div className="container mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center shadow-lg shadow-orange-500/50">
                <span className="text-2xl">⚡</span>
              </div>
              <div>
                <h1 className="text-3xl font-black bg-gradient-to-r from-orange-400 via-red-400 to-pink-400 bg-clip-text text-transparent tracking-tight">
                  SABnzbd Media Tracker
                </h1>
                <p className="text-sm text-gray-400 mt-0.5 font-medium">Real-time download monitoring</p>
              </div>
            </div>

            {/* Failed Downloads Toggle */}
            <button
              onClick={() => setShowFailed(!showFailed)}
              className={`group relative px-6 py-3 rounded-xl font-bold transition-all duration-300 ${
                showFailed
                  ? 'bg-gradient-to-r from-red-500 to-pink-600 text-white shadow-lg shadow-red-500/50 scale-105'
                  : 'bg-white/5 text-gray-300 hover:bg-white/10 border border-white/10 hover:border-white/20 hover:scale-105'
              }`}
            >
              <span className="flex items-center gap-2">
                {showFailed ? (
                  <>✕ Hide Failed</>
                ) : (
                  <>
                    <span className={`${stats.failed > 0 ? 'animate-pulse' : ''}`}>⚠️</span>
                    Failed ({stats.failed || 0})
                  </>
                )}
              </span>
            </button>
          </div>
        </div>
      </header>

      {/* Stats Bar */}
      <StatsBar stats={stats} />

      {/* Navigation */}
      {!showFailed && (
        <Navigation
          activeSection={activeSection}
          setActiveSection={setActiveSection}
          stats={stats}
        />
      )}

      {/* Main Content */}
      <main className="relative container mx-auto px-6 py-8">
        <DownloadSection
          downloads={filteredDownloads}
          section={showFailed ? 'failed' : activeSection}
          isLoading={isLoading}
        />
      </main>

      {/* Footer */}
      <footer className="relative text-center py-8 text-gray-400 text-sm font-medium">
        <div className="flex items-center justify-center gap-2">
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          Auto-refresh every 5s
          <span className="text-gray-600">•</span>
          48h auto-cleanup
        </div>
      </footer>
    </div>
  )
}

export default App
