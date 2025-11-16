import { useEffect, useRef } from 'react'

export default function PrioritySelector({ currentPriority, onSelect, onClose }) {
  const modalRef = useRef()

  const priorities = [
    { value: 'force', numericValue: '3', label: 'Force', color: 'text-red-400', bgColor: 'bg-red-500', icon: '⚡', desc: 'Download immediately' },
    { value: 'high', numericValue: '2', label: 'High', color: 'text-orange-400', bgColor: 'bg-orange-500', icon: '🔥', desc: 'Priority download' },
    { value: 'normal', numericValue: '1', label: 'Normal', color: 'text-blue-400', bgColor: 'bg-blue-500', icon: '➡️', desc: 'Standard queue' },
  ]

  // Normalize currentPriority to match either string or numeric values
  const isCurrentPriority = (priority) => {
    const current = currentPriority?.toLowerCase()
    return current === priority.value || current === priority.numericValue
  }

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (modalRef.current && !modalRef.current.contains(event.target)) {
        onClose()
      }
    }

    const handleEscape = (event) => {
      if (event.key === 'Escape') {
        onClose()
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('keydown', handleEscape)

    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden'

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [onClose])

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
      <div
        ref={modalRef}
        className="bg-gradient-to-br from-gray-900 to-gray-950 border border-white/20 rounded-2xl shadow-2xl overflow-hidden max-w-sm w-full animate-slideUp"
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-white/10">
          <h3 className="text-xl font-bold text-white">Select Priority</h3>
          <p className="text-sm text-gray-400 mt-1">Choose download priority</p>
        </div>

        {/* Priority Options */}
        <div className="p-2">
          {priorities.map(priority => (
            <button
              key={priority.value}
              onClick={(e) => {
                e.stopPropagation()
                console.log('Priority selected:', priority.value)
                onSelect(priority.value)
              }}
              className={`w-full px-4 py-4 text-left transition-all flex items-center gap-4 rounded-xl mb-2 ${
                isCurrentPriority(priority)
                  ? 'bg-white/10 ring-2 ring-blue-500'
                  : 'hover:bg-white/5'
              }`}
            >
              <div className={`text-3xl flex-shrink-0`}>
                {priority.icon}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className={`font-bold ${priority.color}`}>{priority.label}</span>
                  {isCurrentPriority(priority) && (
                    <span className="text-green-400 text-sm">✓ Current</span>
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-0.5">{priority.desc}</p>
              </div>
            </button>
          ))}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-white/10 bg-black/20">
          <button
            onClick={onClose}
            className="w-full px-4 py-2 bg-white/5 hover:bg-white/10 rounded-xl text-sm font-medium text-white transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}
