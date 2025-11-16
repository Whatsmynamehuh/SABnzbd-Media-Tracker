function CompletedItem({ download }) {
  const formatTimeAgo = (dateString) => {
    if (!dateString) return 'Just now'

    const now = new Date()
    const completed = new Date(dateString)
    const diffMs = now - completed
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    return `${diffDays}d ago`
  }

  return (
    <div className="group relative flex-shrink-0 w-40 transition-transform duration-300 hover:scale-105">
      <div className="relative rounded-lg overflow-hidden">
        <div className="relative w-40 h-60 bg-gray-900">
          {download.poster_url ? (
            <img
              src={download.poster_url}
              alt={download.media_title || download.name}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.target.style.display = 'none'
                e.target.parentElement.innerHTML = '<div class="flex items-center justify-center h-full text-5xl">🎬</div>'
              }}
            />
          ) : (
            <div className="flex items-center justify-center h-full text-5xl">🎬</div>
          )}

          {/* Gradient Overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent"></div>

          {/* Checkmark */}
          <div className="absolute top-2 right-2 w-7 h-7 bg-green-500 rounded-full flex items-center justify-center shadow-lg">
            <span className="text-white text-sm">✓</span>
          </div>

          {/* Info */}
          <div className="absolute bottom-0 left-0 right-0 p-2">
            <h3 className="font-bold text-white text-xs mb-1 line-clamp-2">
              {download.media_title || download.name}
            </h3>
            <p className="text-green-400 text-xs font-medium">
              {formatTimeAgo(download.completed_at)}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function CompletedSection({ downloads }) {
  if (downloads.length === 0) {
    return (
      <section>
        <h2 className="text-2xl font-bold text-white mb-6">
          Recently Completed <span className="text-gray-600">(0)</span>
        </h2>
        <div className="bg-jellyseerr-card rounded-2xl p-12 text-center border border-gray-800">
          <div className="text-6xl mb-4">📦</div>
          <h3 className="text-xl font-semibold text-gray-400 mb-2">No completed downloads</h3>
          <p className="text-gray-500">Completed items appear here</p>
        </div>
      </section>
    )
  }

  return (
    <section>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">
          Recently Completed <span className="text-gray-600">({downloads.length})</span>
        </h2>
        <p className="text-sm text-gray-500">Auto-cleanup after 48 hours</p>
      </div>

      <div className="flex gap-3 overflow-x-auto pb-4 scrollbar-hide">
        {downloads.map((download) => (
          <CompletedItem key={download.id} download={download} />
        ))}
      </div>
    </section>
  )
}
