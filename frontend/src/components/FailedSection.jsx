function FailedItem({ download }) {
  return (
    <div className="bg-jellyseerr-card rounded-xl overflow-hidden border border-red-500/50 hover:border-red-500 transition-all">
      <div className="flex gap-4 p-4">
        <div className="relative w-32 h-48 flex-shrink-0 rounded-lg overflow-hidden bg-gray-900">
          {download.poster_url ? (
            <img
              src={download.poster_url}
              alt={download.media_title || download.name}
              className="w-full h-full object-cover"
              onError={(e) => {
                e.target.style.display = 'none'
                e.target.parentElement.innerHTML = '<div class="flex items-center justify-center h-full text-4xl">🎬</div>'
              }}
            />
          ) : (
            <div className="flex items-center justify-center h-full text-4xl">🎬</div>
          )}
        </div>

        <div className="flex-1">
          <h3 className="font-bold text-white text-lg mb-2">
            {download.media_title || download.name}
          </h3>

          {download.failure_reason && (
            <div className="bg-red-500/20 border border-red-500/30 rounded-lg p-3 mb-3">
              <p className="text-red-400 text-sm font-medium">
                {download.failure_reason}
              </p>
            </div>
          )}

          <div className="text-sm text-gray-400 space-y-1">
            {download.year && <p>Year: {download.year}</p>}
            {download.category && <p>Category: {download.category}</p>}
            {download.arr_instance && <p>Source: {download.arr_instance}</p>}
          </div>

          <p className="text-xs text-gray-600 mt-3 font-mono truncate">{download.name}</p>
        </div>
      </div>
    </div>
  )
}

export default function FailedSection({ downloads }) {
  if (downloads.length === 0) {
    return (
      <section>
        <h2 className="text-2xl font-bold text-white mb-6">
          Failed Downloads <span className="text-gray-600">(0)</span>
        </h2>
        <div className="bg-jellyseerr-card rounded-2xl p-12 text-center border border-gray-800">
          <div className="text-6xl mb-4">✅</div>
          <h3 className="text-xl font-semibold text-gray-400 mb-2">No failed downloads</h3>
          <p className="text-gray-500">All downloads completed successfully</p>
        </div>
      </section>
    )
  }

  return (
    <section>
      <h2 className="text-2xl font-bold text-white mb-6">
        Failed Downloads <span className="text-red-500">({downloads.length})</span>
      </h2>

      <div className="space-y-4">
        {downloads.map((download) => (
          <FailedItem key={download.id} download={download} />
        ))}
      </div>
    </section>
  )
}
