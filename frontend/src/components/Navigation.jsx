export default function Navigation({ activeSection, setActiveSection, stats }) {
  const sections = [
    {
      id: 'downloading',
      label: 'Downloading',
      icon: '⬇️',
      count: stats.downloading || 0,
      color: 'orange'
    },
    {
      id: 'queued',
      label: 'Queued',
      icon: '⏸️',
      count: stats.queued || 0,
      color: 'blue'
    },
    {
      id: 'completed',
      label: 'Completed',
      icon: '✅',
      count: stats.completed || 0,
      color: 'green'
    },
  ]

  const colorClasses = {
    orange: {
      active: 'bg-orange-500 text-white',
      hover: 'hover:bg-orange-500/20 hover:text-orange-400',
      border: 'border-orange-500'
    },
    blue: {
      active: 'bg-blue-500 text-white',
      hover: 'hover:bg-blue-500/20 hover:text-blue-400',
      border: 'border-blue-500'
    },
    green: {
      active: 'bg-green-500 text-white',
      hover: 'hover:bg-green-500/20 hover:text-green-400',
      border: 'border-green-500'
    },
  }

  return (
    <nav className="bg-gray-900/30 border-b border-gray-800 sticky top-[73px] z-40">
      <div className="container mx-auto px-4">
        <div className="flex gap-2 overflow-x-auto scrollbar-hide py-4">
          {sections.map(section => {
            const isActive = activeSection === section.id
            const colors = colorClasses[section.color]

            return (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={`px-6 py-3 rounded-lg font-medium transition-all whitespace-nowrap flex items-center gap-2 ${
                  isActive
                    ? `${colors.active} shadow-lg`
                    : `bg-gray-800 text-gray-300 ${colors.hover}`
                }`}
              >
                <span>{section.icon}</span>
                <span>{section.label}</span>
                <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                  isActive ? 'bg-white/20' : 'bg-gray-700'
                }`}>
                  {section.count}
                </span>
              </button>
            )
          })}
        </div>
      </div>
    </nav>
  )
}
