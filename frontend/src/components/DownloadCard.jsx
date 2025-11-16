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
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl overflow-hidden border border-gray-700 hover:border-gray-600 transition-all w-80 flex-shrink-0 shadow-xl">
      {/* Poster */}
      <div className="relative h-48 bg-gray-900 overflow-hidden">
        {download.poster_url ? (
          <img
            src={download.poster_url}
            alt={download.media_title || download.name}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.style.display = 'none'
              e.target.parentElement.classList.add('flex', 'items-center', 'justify-center')
              e.target.parentElement.innerHTML = '<div class="text-6xl">🎬</div>'
            }}
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-6xl">🎬</div>
          </div>
        )}

        {/* Status badge */}
        <div className={`absolute top-2 right-2 px-3 py-1 rounded-full text-xs font-bold ${progressColor} text-white shadow-lg`}>
          {section === 'downloading' ? 'DOWNLOADING' : section.toUpperCase()}
        </div>

        {/* Media type badge */}
        {download.media_type && (
          <div className="absolute top-2 left-2 px-2 py-1 rounded bg-black/70 text-xs font-medium text-white">
            {download.media_type === 'movie' ? '🎬 Movie' : '📺 TV Show'}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Title */}
        <h3 className="font-semibold text-white mb-1 truncate" title={download.media_title || download.name}>
          {download.media_title || download.name}
        </h3>

        {/* Year and Source */}
        <div className="flex items-center gap-2 text-xs text-gray-400 mb-3">
          {download.year && <span>{download.year}</span>}
          {download.arr_instance && (
            <>
              <span>•</span>
              <span className="truncate">{download.arr_instance}</span>
            </>
          )}
        </div>

        {/* Progress Bar */}
        {section !== 'completed' && (
          <div className="mb-3">
            <div className="flex justify-between text-xs text-gray-400 mb-1">
              <span>{download.progress?.toFixed(1)}%</span>
              {download.time_left && download.status === 'downloading' && (
                <span>{download.time_left}</span>
              )}
            </div>
            <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
              <div
                className={`h-full ${progressColor} transition-all duration-300`}
                style={{ width: `${download.progress || 0}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-2 gap-2 text-xs mb-3">
          <div>
            <span className="text-gray-500">Size:</span>
            <span className="text-gray-300 ml-1 font-medium">{formatSize(download.size_total)}</span>
          </div>
          {download.size_left > 0 && (
            <div>
              <span className="text-gray-500">Left:</span>
              <span className="text-gray-300 ml-1 font-medium">{formatSize(download.size_left)}</span>
            </div>
          )}
          {download.speed > 0 && (
            <div className="col-span-2">
              <span className="text-gray-500">Speed:</span>
              <span className="text-orange-400 ml-1 font-medium">{formatSpeed(download.speed)}</span>
            </div>
          )}
          {download.category && (
            <div className="col-span-2">
              <span className="text-gray-500">Category:</span>
              <span className="text-gray-300 ml-1">{download.category}</span>
            </div>
          )}
        </div>

        {/* Priority (for queued items) */}
        {section === 'queued' && (
          <div className="relative">
            <button
              onClick={() => setShowPriority(!showPriority)}
              className="w-full px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm font-medium transition-colors flex items-center justify-between"
            >
              <span>Priority: {download.priority || 'Normal'}</span>
              <span>{showPriority ? '▲' : '▼'}</span>
            </button>

            {showPriority && (
              <PrioritySelector
                currentPriority={download.priority}
                onSelect={handlePriorityChange}
                onClose={() => setShowPriority(false)}
              />
            )}
          </div>
        )}

        {/* Failed reason */}
        {download.failed && download.failure_reason && (
          <div className="mt-3 p-2 bg-red-500/10 border border-red-500/30 rounded text-xs text-red-400">
            {download.failure_reason}
          </div>
        )}

        {/* Filename (small print) */}
        <div className="mt-3 pt-3 border-t border-gray-700">
          <p className="text-xs text-gray-500 truncate" title={download.name}>
            {download.name}
          </p>
        </div>
      </div>
    </div>
  )
}
