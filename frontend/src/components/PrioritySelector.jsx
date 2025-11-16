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
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-3 sm:p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
      <div
        ref={modalRef}
        className="bg-gradient-to-br from-gray-900 to-gray-950 border border-white/20 rounded-2xl shadow-2xl overflow-hidden max-w-md w-full animate-slideUp"
      >
        {/* Header */}
        <div className="px-4 sm:px-6 py-4 sm:py-5 border-b border-white/10">
          <h3 className="text-lg sm:text-xl font-bold text-white">Select Priority</h3>
          <p className="text-xs sm:text-sm text-gray-400 mt-1">Choose download priority</p>
        </div>

        {/* Priority Options */}
        <div className="p-3 sm:p-4">
          {priorities.map(priority => (
            <button
              key={priority.value}
              onClick={(e) => {
                e.stopPropagation()
                console.log('Priority selected:', priority.value)
                onSelect(priority.value)
              }}
              className={`w-full px-4 sm:px-5 py-4 sm:py-5 text-left transition-all flex items-center gap-3 sm:gap-4 rounded-xl mb-2 sm:mb-3 active:scale-95 ${
                isCurrentPriority(priority)
                  ? 'bg-white/10 ring-2 ring-blue-500'
                  : 'hover:bg-white/5 active:bg-white/10'
              }`}
            >
              <div className="text-3xl sm:text-4xl flex-shrink-0">
                {priority.icon}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className={`font-bold text-base sm:text-lg ${priority.color}`}>{priority.label}</span>
                  {isCurrentPriority(priority) && (
                    <span className="text-green-400 text-xs sm:text-sm">✓ Current</span>
                  )}
                </div>
                <p className="text-xs sm:text-sm text-gray-500 mt-0.5">{priority.desc}</p>
              </div>
            </button>
          ))}
        </div>

        {/* Footer */}
        <div className="px-4 sm:px-6 py-3 sm:py-4 border-t border-white/10 bg-black/20">
          <button
            onClick={onClose}
            className="w-full px-4 py-3 sm:py-3.5 bg-white/5 hover:bg-white/10 active:bg-white/15 rounded-xl text-sm sm:text-base font-medium text-white transition-colors active:scale-95"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  )
}
