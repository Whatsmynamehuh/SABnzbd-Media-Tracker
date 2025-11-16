import { useEffect, useRef } from 'react'

export default function PrioritySelector({ currentPriority, onSelect, onClose }) {
  const ref = useRef()

  const priorities = [
    { value: 'force', label: 'Force', color: 'text-red-400', icon: '⚡' },
    { value: 'high', label: 'High', color: 'text-orange-400', icon: '🔥' },
    { value: 'normal', label: 'Normal', color: 'text-blue-400', icon: '➡️' },
    { value: 'low', label: 'Low', color: 'text-gray-400', icon: '⬇️' },
    { value: 'paused', label: 'Paused', color: 'text-gray-500', icon: '⏸️' },
  ]

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
          onClick={() => onSelect(priority.value)}
          className={`w-full px-3 py-2 text-left text-sm transition-colors flex items-center gap-2 ${
            currentPriority?.toLowerCase() === priority.value
              ? 'bg-gray-700'
              : 'hover:bg-gray-700/50'
          }`}
        >
          <span>{priority.icon}</span>
          <span className={priority.color}>{priority.label}</span>
          {currentPriority?.toLowerCase() === priority.value && (
            <span className="ml-auto text-green-400">✓</span>
          )}
        </button>
      ))}
    </div>
  )
}
