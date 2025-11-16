import { useEffect, useRef } from 'react'

export default function PrioritySelector({ currentPriority, onSelect, onClose }) {
  const ref = useRef()

  const priorities = [
    { value: 'force', numericValue: '3', label: 'Force', color: 'text-red-400', bgColor: 'bg-red-500', icon: '⚡' },
    { value: 'high', numericValue: '2', label: 'High', color: 'text-orange-400', bgColor: 'bg-orange-500', icon: '🔥' },
    { value: 'normal', numericValue: '1', label: 'Normal', color: 'text-blue-400', bgColor: 'bg-blue-500', icon: '➡️' },
  ]

  // Normalize currentPriority to match either string or numeric values
  const isCurrentPriority = (priority) => {
    const current = currentPriority?.toLowerCase()
    return current === priority.value || current === priority.numericValue
  }

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (ref.current && !ref.current.contains(event.target)) {
        onClose()
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [onClose])

  return (
    <div ref={ref} className="absolute bottom-full mb-2 left-0 right-0 bg-gray-800 border border-gray-700 rounded-lg shadow-xl overflow-hidden z-50">
      {priorities.map(priority => (
        <button
          key={priority.value}
          onClick={(e) => {
            e.stopPropagation()
            console.log('Priority selected:', priority.value)
            onSelect(priority.value)
          }}
          className={`w-full px-3 py-2 text-left text-sm transition-colors flex items-center gap-2 ${
            isCurrentPriority(priority)
              ? 'bg-gray-700'
              : 'hover:bg-gray-700/50'
          }`}
        >
          <span>{priority.icon}</span>
          <span className={priority.color}>{priority.label}</span>
          {isCurrentPriority(priority) && (
            <span className="ml-auto text-green-400">✓</span>
          )}
        </button>
      ))}
    </div>
  )
}
