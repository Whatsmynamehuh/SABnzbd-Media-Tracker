export default function StatsBar({ stats }) {
  return (
    <div className="relative backdrop-blur-xl bg-gradient-to-r from-white/5 to-white/[0.02] border-b border-white/10">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-center gap-12">
          {/* Downloading */}
          <div className="group flex items-center gap-3 px-4 py-2 rounded-xl bg-gradient-to-br from-orange-500/10 to-transparent border border-orange-500/20 hover:border-orange-500/40 transition-all">
            <div className="relative">
              <div className="w-3 h-3 bg-orange-500 rounded-full animate-pulse"></div>
              <div className="absolute inset-0 w-3 h-3 bg-orange-500 rounded-full animate-ping"></div>
            </div>
            <span className="text-gray-400 font-medium">Downloading</span>
            <span className="font-black text-xl bg-gradient-to-r from-orange-400 to-red-400 bg-clip-text text-transparent">
              {stats.downloading || 0}
            </span>
          </div>

          {/* Queued */}
          <div className="group flex items-center gap-3 px-4 py-2 rounded-xl bg-gradient-to-br from-blue-500/10 to-transparent border border-blue-500/20 hover:border-blue-500/40 transition-all">
            <div className="w-3 h-3 bg-blue-500 rounded-full shadow-lg shadow-blue-500/50"></div>
            <span className="text-gray-400 font-medium">Queued</span>
            <span className="font-black text-xl bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              {stats.queued || 0}
            </span>
          </div>

          {/* Completed */}
          <div className="group flex items-center gap-3 px-4 py-2 rounded-xl bg-gradient-to-br from-green-500/10 to-transparent border border-green-500/20 hover:border-green-500/40 transition-all">
            <div className="w-3 h-3 bg-green-500 rounded-full shadow-lg shadow-green-500/50"></div>
            <span className="text-gray-400 font-medium">Completed</span>
            <span className="font-black text-xl bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent">
              {stats.completed || 0}
            </span>
          </div>

          {/* Speed */}
          {stats.total_speed > 0 && (
            <div className="flex items-center gap-3 px-4 py-2 rounded-xl bg-gradient-to-br from-purple-500/10 to-transparent border border-purple-500/20">
              <span className="text-2xl">⚡</span>
              <div className="flex flex-col">
                <span className="text-xs text-gray-500 font-medium">Total Speed</span>
                <span className="font-black text-lg bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                  {stats.total_speed} MB/s
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
