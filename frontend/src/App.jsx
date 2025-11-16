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
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
      {/* Header */}
      <header className="bg-gray-900/50 backdrop-blur-sm border-b border-gray-800 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-orange-500 to-red-500 bg-clip-text text-transparent">
                SABnzbd Media Tracker
              </h1>
              <p className="text-sm text-gray-400 mt-1">Real-time download monitoring</p>
            </div>

            {/* Failed Downloads Toggle */}
            <button
              onClick={() => setShowFailed(!showFailed)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                showFailed
                  ? 'bg-red-500 text-white'
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              {showFailed ? '✕ Hide Failed' : `⚠️ Failed (${stats.failed || 0})`}
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
      <main className="container mx-auto px-4 py-6">
        <DownloadSection
          downloads={filteredDownloads}
          section={showFailed ? 'failed' : activeSection}
          isLoading={isLoading}
        />
      </main>

      {/* Footer */}
      <footer className="text-center py-6 text-gray-500 text-sm">
        Auto-refreshing every 5 seconds • Completed items auto-cleanup after 48 hours
      </footer>
    </div>
  )
}

export default App
