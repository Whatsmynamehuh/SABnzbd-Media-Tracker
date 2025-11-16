import { useState } from 'react'
import axios from 'axios'
import PrioritySelector from './PrioritySelector'

function QueueItem({ download, position }) {
  const [isToggling, setIsToggling] = useState(false)
  const [showPrioritySelector, setShowPrioritySelector] = useState(false)

  const formatSize = (mb) => {
    if (!mb) return 'N/A'
    if (mb > 1024) return `${(mb / 1024).toFixed(2)} GB`
    return `${mb.toFixed(2)} MB`
  }

  // Map SABnzbd priority values to labels
  const getPriorityInfo = (priority) => {
    const priorityMap = {
      '3': { label: 'FORCE', color: 'bg-red-500', ring: 'ring-red-500', icon: '⚡' },
      'force': { label: 'FORCE', color: 'bg-red-500', ring: 'ring-red-500', icon: '⚡' },
      '2': { label: 'HIGH', color: 'bg-orange-500', ring: 'ring-orange-500', icon: '🔥' },
      'high': { label: 'HIGH', color: 'bg-orange-500', ring: 'ring-orange-500', icon: '🔥' },
      '1': { label: 'NORMAL', color: 'bg-gray-800/70', ring: '', icon: '➡️' },
      'normal': { label: 'NORMAL', color: 'bg-gray-800/70', ring: '', icon: '➡️' },
    }
    return priorityMap[priority?.toLowerCase()] || priorityMap['normal']
  }

  const priorityInfo = getPriorityInfo(download.priority)
  const isHighPriority = priorityInfo.label === 'FORCE' || priorityInfo.label === 'HIGH'

  const handlePrioritySelect = async (newPriority) => {
    setIsToggling(true)
    setShowPrioritySelector(false)
    try {
      await axios.post(`/api/downloads/${download.id}/priority`, { priority: newPriority })
    } catch (error) {
      console.error('Failed to update priority:', error)
    }
    setTimeout(() => setIsToggling(false), 300)
  }

  return (
    <>
      <div
        onClick={(e) => {
          e.stopPropagation()
          setShowPrioritySelector(!showPrioritySelector)
        }}
        className={`group relative flex-shrink-0 w-48 cursor-pointer transition-all duration-300 ${
          isToggling ? 'scale-95' : 'hover:scale-105'
        } ${isHighPriority ? 'order-0' : 'order-1'}`}
      >

      {/* Poster */}
      <div className={`relative rounded-xl overflow-hidden ${
        priorityInfo.ring ? `ring-2 ${priorityInfo.ring} shadow-lg ${priorityInfo.ring.replace('ring-', 'shadow-')}/50` : ''
      }`}>
        <div className="relative w-48 h-72 bg-gray-900">
          {download.poster_url ? (
            <img
              src={download.poster_url}
              alt={download.media_title || download.name}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.target.style.display = 'none'
                e.target.parentElement.innerHTML = '<div class="flex items-center justify-center h-full text-6xl">🎬</div>'
              }}
            />
          ) : (
            <div className="flex items-center justify-center h-full text-6xl">🎬</div>
          )}

          {/* Gradient Overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent"></div>

          {/* Position Badge */}
          <div className="absolute top-2 left-2 w-8 h-8 bg-black/70 backdrop-blur-sm rounded-full flex items-center justify-center font-bold text-sm">
            #{position}
          </div>

          {/* Priority Badge */}
          <div className={`absolute top-2 right-2 px-3 py-1 rounded-lg font-bold text-xs text-white shadow-lg flex items-center gap-1 ${priorityInfo.color}`}>
            <span>{priorityInfo.icon}</span>
            <span>{priorityInfo.label}</span>
          </div>

          {/* Info Overlay */}
          <div className="absolute bottom-0 left-0 right-0 p-3">
            <h3 className="font-bold text-white text-sm mb-1 line-clamp-2">
              {download.media_title || download.name}
            </h3>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              {download.year && <span>{download.year}</span>}
              {download.media_type && (
                <>
                  <span>•</span>
                  <span>{download.media_type === 'movie' ? '🎬' : '📺'}</span>
                </>
              )}
              {download.category && (
                <>
                  <span>•</span>
                  <span className="text-blue-400">{download.category}</span>
                </>
              )}
            </div>
            <p className="text-gray-400 text-xs mt-1">{formatSize(download.size_total)}</p>
          </div>
        </div>

        {/* Hover hint */}
        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <p className="text-white font-bold text-sm">
            Click to Change Priority
          </p>
        </div>
      </div>
    </div>

    {/* Priority Modal (rendered at top level) */}
    {showPrioritySelector && (
      <PrioritySelector
        currentPriority={download.priority}
        onSelect={handlePrioritySelect}
        onClose={() => setShowPrioritySelector(false)}
      />
    )}
    </>
  )
}

export default function QueueSection({ downloads }) {
  if (downloads.length === 0) {
    return (
      <section>
        <h2 className="text-2xl font-bold text-white mb-6">
          Queue <span className="text-gray-600">(0)</span>
        </h2>
        <div className="bg-jellyseerr-card rounded-2xl p-12 text-center border border-gray-800">
          <div className="text-6xl mb-4">📭</div>
          <h3 className="text-xl font-semibold text-gray-400 mb-2">Queue is empty</h3>
          <p className="text-gray-500">No downloads waiting</p>
        </div>
      </section>
    )
  }

  return (
    <section>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-white">
          Queue <span className="text-gray-600">({downloads.length})</span>
        </h2>
        <p className="text-sm text-gray-500">
          Click to change priority • Force / High / Normal
        </p>
      </div>

      {/* Info Banner */}
      <div className="mb-6 px-4 py-3 bg-blue-500/10 border border-blue-500/30 rounded-xl">
        <p className="text-xs text-blue-300">
          💡 <span className="font-semibold">Priority Note:</span> Items at position #1 are automatically set to <span className="font-bold">FORCE</span> by SABnzbd while actively downloading
        </p>
      </div>

      <div
        className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide"
        style={{
          WebkitOverflowScrolling: 'touch',
          touchAction: 'pan-x',
          scrollBehavior: 'smooth'
        }}
      >
        {downloads.map((download) => (
          <QueueItem
            key={download.id}
            download={download}
            position={download.queue_position || '?'}
          />
        ))}
      </div>
    </section>
  )
}
