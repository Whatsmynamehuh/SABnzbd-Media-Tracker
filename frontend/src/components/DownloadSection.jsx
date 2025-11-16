import DownloadCard from './DownloadCard'

export default function DownloadSection({ downloads, section, isLoading }) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto"></div>
          <p className="text-gray-400 mt-4">Loading downloads...</p>
        </div>
      </div>
    )
  }

  if (downloads.length === 0) {
    const emptyMessages = {
      downloading: {
        icon: '⬇️',
        title: 'No active downloads',
        message: 'Downloads will appear here when they start'
      },
      queued: {
        icon: '⏸️',
        title: 'Queue is empty',
        message: 'No downloads waiting in queue'
      },
      completed: {
        icon: '✅',
        title: 'No completed downloads',
        message: 'Completed downloads appear here (auto-cleaned after 48 hours)'
      },
      failed: {
        icon: '⚠️',
        title: 'No failed downloads',
        message: 'Failed downloads will appear here'
      }
    }

    const empty = emptyMessages[section] || emptyMessages.downloading

    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-center">
          <div className="text-6xl mb-4">{empty.icon}</div>
          <h3 className="text-xl font-semibold text-gray-300 mb-2">{empty.title}</h3>
          <p className="text-gray-500">{empty.message}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto scrollbar-hide">
      <div className="flex gap-6 pb-6" style={{ minWidth: 'min-content' }}>
        {downloads.map(download => (
          <DownloadCard key={download.id} download={download} section={section} />
        ))}
      </div>
    </div>
  )
}
