export default function HeroDownload({ download, isLoading }) {
  if (isLoading) {
    return (
      <section className="w-full max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold text-white mb-6">Downloading Now</h2>
        <div className="bg-jellyseerr-card rounded-2xl p-8 animate-pulse">
          <div className="flex gap-6">
            <div className="w-64 h-96 bg-gray-800 rounded-lg"></div>
            <div className="flex-1 space-y-4">
              <div className="h-8 bg-gray-800 rounded w-3/4"></div>
              <div className="h-4 bg-gray-800 rounded w-1/2"></div>
            </div>
          </div>
        </div>
      </section>
    )
  }

  if (!download) {
    return (
      <section className="w-full max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold text-white mb-6">Downloading Now</h2>
        <div className="bg-jellyseerr-card rounded-2xl p-12 text-center border border-gray-800">
          <div className="text-6xl mb-4">💤</div>
          <h3 className="text-xl font-semibold text-gray-400 mb-2">Nothing downloading</h3>
          <p className="text-gray-500">Queue is idle</p>
        </div>
      </section>
    )
  }

  const formatSize = (mb) => {
    if (!mb) return 'N/A'
    if (mb > 1024) return `${(mb / 1024).toFixed(2)} GB`
    return `${mb.toFixed(2)} MB`
  }

  return (
    <section className="w-full max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold text-white mb-6">Downloading Now</h2>

      <div className="bg-jellyseerr-card rounded-2xl overflow-hidden border border-orange-500/50 shadow-2xl shadow-orange-500/20">
        <div className="flex flex-col md:flex-row gap-6 p-6">
          {/* Large Poster */}
          <div className="relative w-full md:w-80 h-[480px] flex-shrink-0 rounded-xl overflow-hidden bg-gray-900">
            {download.poster_url ? (
              <img
                src={download.poster_url}
                alt={download.media_title || download.name}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.style.display = 'none'
                  e.target.parentElement.innerHTML = '<div class="flex items-center justify-center h-full text-8xl">🎬</div>'
                }}
              />
            ) : (
              <div className="flex items-center justify-center h-full text-8xl">🎬</div>
            )}

            {/* Status Badge */}
            <div className="absolute top-3 right-3 px-4 py-2 bg-orange-500 rounded-lg font-bold text-sm shadow-lg animate-pulse">
              DOWNLOADING
            </div>

            {/* Media Type */}
            {download.media_type && (
              <div className="absolute top-3 left-3 px-3 py-1.5 bg-black/70 backdrop-blur-sm rounded-lg text-xs font-bold">
                {download.media_type === 'movie' ? '🎬 Movie' : '📺 TV Show'}
              </div>
            )}
          </div>

          {/* Details */}
          <div className="flex-1 flex flex-col justify-center space-y-6">
            {/* Title */}
            <div>
              <h3 className="text-3xl font-bold text-white mb-2">
                {download.media_title || download.name}
              </h3>
              {download.year && (
                <p className="text-gray-400 text-lg">{download.year}</p>
              )}
              {download.arr_instance && (
                <p className="text-gray-500 text-sm mt-1">{download.arr_instance}</p>
              )}
            </div>

            {/* Progress */}
            <div>
              <div className="flex justify-between items-end mb-2">
                <span className="text-5xl font-black text-orange-400">
                  {download.progress?.toFixed(1)}%
                </span>
                {download.time_left && (
                  <span className="text-lg text-gray-400">⏱️ {download.time_left}</span>
                )}
              </div>

              {/* Progress Bar */}
              <div className="relative h-4 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-orange-500 to-red-500 transition-all duration-500"
                  style={{ width: `${download.progress || 0}%` }}
                ></div>
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer"></div>
              </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-900/50 rounded-xl p-4 border border-gray-800">
                <p className="text-gray-500 text-sm mb-1">Speed</p>
                <p className="text-2xl font-bold text-orange-400">
                  {download.speed?.toFixed(2) || '0.00'} MB/s
                </p>
              </div>

              <div className="bg-gray-900/50 rounded-xl p-4 border border-gray-800">
                <p className="text-gray-500 text-sm mb-1">Downloaded</p>
                <p className="text-xl font-bold text-white">
                  {formatSize(download.size_total - (download.size_left || 0))} / {formatSize(download.size_total)}
                </p>
              </div>

              {download.category && (
                <div className="col-span-2 bg-gray-900/50 rounded-xl p-4 border border-gray-800">
                  <p className="text-gray-500 text-sm mb-1">Category</p>
                  <p className="text-lg font-medium text-white">{download.category}</p>
                </div>
              )}
            </div>

            {/* Filename */}
            <div className="pt-4 border-t border-gray-800">
              <p className="text-xs text-gray-600 font-mono truncate">{download.name}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
