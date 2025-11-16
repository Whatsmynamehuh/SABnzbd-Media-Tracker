import { useState } from 'react'
import axios from 'axios'
import PrioritySelector from './PrioritySelector'

export default function DownloadCard({ download, section }) {
  const [showPriority, setShowPriority] = useState(false)

  const progressColor = {
    downloading: 'bg-orange-500',
    queued: 'bg-blue-500',
    completed: 'bg-green-500',
    failed: 'bg-red-500'
  }[section] || 'bg-gray-500'

  const gradientColor = {
    downloading: 'from-orange-500 to-red-600',
    queued: 'from-blue-500 to-cyan-600',
    completed: 'from-green-500 to-emerald-600',
    failed: 'from-red-500 to-pink-600'
  }[section] || 'from-gray-500 to-gray-600'

  const formatSize = (mb) => {
    if (!mb) return 'N/A'
    if (mb > 1024) return `${(mb / 1024).toFixed(2)} GB`
    return `${mb.toFixed(2)} MB`
  }

  const formatSpeed = (mbps) => {
    if (!mbps || mbps === 0) return ''
    return `${mbps.toFixed(2)} MB/s`
  }

  const handlePriorityChange = async (priority) => {
    try {
      await axios.post(`/api/downloads/${download.id}/priority`, { priority })
      setShowPriority(false)
    } catch (error) {
      console.error('Failed to update priority:', error)
    }
  }

  return (
    <div className="group relative bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-3xl overflow-hidden border border-white/20 hover:border-white/40 transition-all duration-500 w-80 flex-shrink-0 shadow-2xl hover:shadow-3xl hover:scale-105 hover:-translate-y-2">
      {/* Poster */}
      <div className="relative h-64 bg-gradient-to-br from-gray-900 to-gray-950 overflow-hidden">
        {download.poster_url ? (
          <img
            src={download.poster_url}
            alt={download.media_title || download.name}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
            onError={(e) => {
              e.target.style.display = 'none'
              e.target.parentElement.classList.add('flex', 'items-center', 'justify-center')
              e.target.parentElement.innerHTML = '<div class="text-7xl animate-pulse">🎬</div>'
            }}
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-7xl animate-pulse">🎬</div>
          </div>
        )}

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent"></div>

        {/* Status badge */}
        <div className={`absolute top-3 right-3 px-4 py-2 rounded-xl text-xs font-black bg-gradient-to-r ${gradientColor} text-white shadow-2xl backdrop-blur-sm border border-white/20 ${section === 'downloading' ? 'animate-pulse' : ''}`}>
          {section === 'downloading' ? 'DOWNLOADING' : section.toUpperCase()}
        </div>

        {/* Media type badge */}
        {download.media_type && (
          <div className="absolute top-3 left-3 px-3 py-2 rounded-xl bg-black/50 backdrop-blur-md text-xs font-bold text-white border border-white/20">
            {download.media_type === 'movie' ? '🎬 Movie' : '📺 TV Show'}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-5">
        {/* Title */}
        <h3 className="font-bold text-lg text-white mb-2 truncate" title={download.media_title || download.name}>
          {download.media_title || download.name}
        </h3>

        {/* Year and Source */}
        <div className="flex items-center gap-2 text-xs text-gray-400 mb-4">
          {download.year && (
            <span className="px-2 py-1 bg-white/10 rounded-lg font-medium">{download.year}</span>
          )}
          {download.arr_instance && (
            <span className="px-2 py-1 bg-white/10 rounded-lg font-medium truncate">
              {download.arr_instance}
            </span>
          )}
        </div>

        {/* Progress Bar */}
        {section !== 'completed' && (
          <div className="mb-4">
            <div className="flex justify-between text-xs font-bold text-gray-300 mb-2">
              <span>{download.progress?.toFixed(1)}%</span>
              {download.time_left && download.status === 'downloading' && (
                <span className="text-orange-400">{download.time_left}</span>
              )}
            </div>
            <div className="relative h-3 bg-white/10 rounded-full overflow-hidden backdrop-blur-sm">
              <div
                className={`h-full bg-gradient-to-r ${gradientColor} transition-all duration-500 shadow-lg`}
                style={{ width: `${download.progress || 0}%` }}
              ></div>
              {section === 'downloading' && (
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer"></div>
              )}
            </div>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="px-3 py-2 bg-white/5 rounded-xl border border-white/10">
            <span className="text-xs text-gray-500 block">Size</span>
            <span className="text-sm text-white font-bold">{formatSize(download.size_total)}</span>
          </div>
          {download.size_left > 0 && (
            <div className="px-3 py-2 bg-white/5 rounded-xl border border-white/10">
              <span className="text-xs text-gray-500 block">Left</span>
              <span className="text-sm text-white font-bold">{formatSize(download.size_left)}</span>
            </div>
          )}
          {download.speed > 0 && (
            <div className="col-span-2 px-3 py-2 bg-gradient-to-r from-orange-500/20 to-red-500/20 rounded-xl border border-orange-500/30">
              <span className="text-xs text-orange-300 block">Speed</span>
              <span className="text-lg font-black bg-gradient-to-r from-orange-400 to-red-400 bg-clip-text text-transparent">
                {formatSpeed(download.speed)}
              </span>
            </div>
          )}
          {download.category && (
            <div className="col-span-2 px-3 py-2 bg-white/5 rounded-xl border border-white/10">
              <span className="text-xs text-gray-500 block">Category</span>
              <span className="text-sm text-white font-medium">{download.category}</span>
            </div>
          )}
        </div>

        {/* Priority (for queued items) */}
        {section === 'queued' && (
          <div className="mb-4">
            <button
              onClick={(e) => {
                e.stopPropagation()
                setShowPriority(!showPriority)
              }}
              className="w-full px-4 py-3 bg-gradient-to-r from-blue-500/20 to-cyan-500/20 hover:from-blue-500/30 hover:to-cyan-500/30 rounded-xl text-sm font-bold transition-all border border-blue-500/30 hover:border-blue-500/50 flex items-center justify-between"
            >
              <span className="text-white">Priority: {download.priority || 'Normal'}</span>
              <span className="text-blue-400">⚙️</span>
            </button>
          </div>
        )}

        {/* Priority Modal (rendered at top level) */}
        {showPriority && (
          <PrioritySelector
            currentPriority={download.priority}
            onSelect={handlePriorityChange}
            onClose={() => setShowPriority(false)}
          />
        )}

        {/* Failed reason */}
        {download.failed && download.failure_reason && (
          <div className="mb-4 p-3 bg-gradient-to-r from-red-500/20 to-pink-500/20 border border-red-500/40 rounded-xl">
            <span className="text-xs font-bold text-red-300 block mb-1">Error:</span>
            <span className="text-xs text-red-400">{download.failure_reason}</span>
          </div>
        )}

        {/* Filename (small print) */}
        <div className="pt-4 border-t border-white/10">
          <p className="text-xs text-gray-500 truncate font-medium" title={download.name}>
            {download.name}
          </p>
        </div>
      </div>
    </div>
  )
}
