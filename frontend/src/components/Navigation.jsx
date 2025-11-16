export default function Navigation({ activeSection, setActiveSection, stats }) {
  const sections = [
    {
      id: 'downloading',
      label: 'Downloading',
      icon: '⬇️',
      count: stats.downloading || 0,
      gradient: 'from-orange-500 to-red-600',
      glowColor: 'orange'
    },
    {
      id: 'queued',
      label: 'Queued',
      icon: '⏸️',
      count: stats.queued || 0,
      gradient: 'from-blue-500 to-cyan-600',
      glowColor: 'blue'
    },
    {
      id: 'completed',
      label: 'Completed',
      icon: '✅',
      count: stats.completed || 0,
      gradient: 'from-green-500 to-emerald-600',
      glowColor: 'green'
    },
  ]

  return (
    <nav className="relative backdrop-blur-xl bg-white/5 border-b border-white/10 sticky top-[89px] z-40">
      <div className="container mx-auto px-6">
        <div
          className="flex gap-4 overflow-x-auto scrollbar-hide py-6"
          style={{
            WebkitOverflowScrolling: 'touch',
            touchAction: 'pan-x',
            scrollBehavior: 'smooth'
          }}
        >
          {sections.map(section => {
            const isActive = activeSection === section.id

            return (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={`group relative px-8 py-4 rounded-2xl font-bold transition-all duration-300 whitespace-nowrap flex items-center gap-3 ${
                  isActive
                    ? `bg-gradient-to-r ${section.gradient} text-white shadow-2xl shadow-${section.glowColor}-500/50 scale-110`
                    : 'bg-white/5 text-gray-300 hover:bg-white/10 border border-white/10 hover:border-white/20 hover:scale-105'
                }`}
              >
                <span className={`text-2xl ${isActive ? 'animate-bounce' : 'group-hover:scale-125 transition-transform'}`}>
                  {section.icon}
                </span>
                <span className="text-lg">{section.label}</span>
                <span className={`min-w-[2rem] h-8 flex items-center justify-center px-3 rounded-xl text-sm font-black ${
                  isActive
                    ? 'bg-white/20 backdrop-blur-sm'
                    : 'bg-white/10 group-hover:bg-white/20'
                }`}>
                  {section.count}
                </span>

                {/* Glow effect for active */}
                {isActive && (
                  <div className={`absolute inset-0 rounded-2xl bg-gradient-to-r ${section.gradient} blur-xl opacity-50 -z-10`}></div>
                )}
              </button>
            )
          })}
        </div>
      </div>
    </nav>
  )
}
