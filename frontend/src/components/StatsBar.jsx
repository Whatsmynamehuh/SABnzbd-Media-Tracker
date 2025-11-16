export default function StatsBar({ stats }) {
  return (
    <div className="bg-gray-900/30 border-b border-gray-800">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-center gap-8 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-orange-500 rounded-full animate-pulse"></div>
            <span className="text-gray-400">Downloading:</span>
            <span className="font-bold text-orange-400">{stats.downloading || 0}</span>
          </div>

          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span className="text-gray-400">Queued:</span>
            <span className="font-bold text-blue-400">{stats.queued || 0}</span>
          </div>

          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-gray-400">Completed:</span>
            <span className="font-bold text-green-400">{stats.completed || 0}</span>
          </div>

          {stats.total_speed > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-gray-400">Speed:</span>
              <span className="font-bold text-orange-400">{stats.total_speed} MB/s</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
