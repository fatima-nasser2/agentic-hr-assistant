import { useState, useEffect } from 'react'
import { PanelLeft } from 'lucide-react'
import clsx from 'clsx'
import Header from './Header'
import Sidebar from './Sidebar'
import ChatWindow from '../chat/ChatWindow'
import { useConversations } from '../../hooks/useConversations'
import { useMediaQuery } from '../../hooks/useMediaQuery'

const MIN_WIDTH = 200
const MAX_WIDTH = 480
const DEFAULT_WIDTH = 260

export default function Layout({ employee, darkMode, onToggleDark, onLogout }) {
  const isMobile = useMediaQuery('(max-width: 767px)')
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile)
  const [sidebarWidth, setSidebarWidth] = useState(DEFAULT_WIDTH)
  const [isResizing, setIsResizing] = useState(false)

  useEffect(() => {
    setSidebarOpen(!isMobile)
  }, [isMobile])

  const {
    conversations,
    activeId,
    activeConversation,
    newConversation,
    switchConversation,
    sendMessage,
    clearChat,
    renameConversation,
    deleteConversation,
    giveFeedback,
  } = useConversations()

  const handleSwitch = (id) => {
    switchConversation(id)
    if (isMobile) setSidebarOpen(false)
  }

  const startResize = (e) => {
    e.preventDefault()
    setIsResizing(true)
    const startX = e.clientX
    const startWidth = sidebarWidth

    const onMouseMove = (e) => {
      const next = Math.min(Math.max(startWidth + (e.clientX - startX), MIN_WIDTH), MAX_WIDTH)
      setSidebarWidth(next)
    }

    const onMouseUp = () => {
      setIsResizing(false)
      window.removeEventListener('mousemove', onMouseMove)
      window.removeEventListener('mouseup', onMouseUp)
    }

    window.addEventListener('mousemove', onMouseMove)
    window.addEventListener('mouseup', onMouseUp)
  }

  return (
    <div className={clsx(
      'h-screen flex flex-col bg-gray-50 dark:bg-gray-950',
      isResizing && 'select-none cursor-ew-resize'
    )}>
      <Header
        darkMode={darkMode}
        onToggleDark={onToggleDark}
      />

      <div className="flex-1 flex overflow-hidden relative">

        {/* Mobile backdrop */}
        {isMobile && sidebarOpen && (
          <div
            className="absolute inset-0 z-40 bg-black/40"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Sidebar wrapper — push on desktop, overlay on mobile */}
        <div
          className={clsx(
            isMobile
              ? clsx(
                  'absolute left-0 top-0 h-full z-50 transition-transform duration-200',
                  sidebarOpen ? 'translate-x-0' : '-translate-x-full'
                )
              : clsx(
                  'shrink-0 overflow-hidden z-10',
                  sidebarOpen && 'shadow-[4px_0_16px_rgba(0,0,0,0.07)] dark:shadow-[4px_0_16px_rgba(0,0,0,0.3)]',
                  !isResizing && 'transition-[width] duration-200'
                )
          )}
          style={!isMobile ? { width: sidebarOpen ? sidebarWidth : 0 } : undefined}
        >
          <Sidebar
            isMobile={isMobile}
            conversations={conversations}
            activeId={activeId}
            onNew={newConversation}
            onSwitch={handleSwitch}
            onCollapse={() => setSidebarOpen(false)}
            onRename={renameConversation}
            onDelete={deleteConversation}
            employee={employee}
            onLogout={onLogout}
          />
        </div>

        {/* Resize handle — desktop only, sits on top of the shadow */}
        {!isMobile && sidebarOpen && (
          <div
            onMouseDown={startResize}
            className="w-1 shrink-0 self-stretch cursor-ew-resize z-20"
          />
        )}

        <main className="flex-1 flex flex-col min-h-0 overflow-hidden relative">
          {!sidebarOpen && (
            <button
              onClick={() => setSidebarOpen(true)}
              aria-label="Open sidebar"
              className="absolute top-3 left-3 z-10 p-1.5 rounded-lg text-gray-400 dark:text-gray-600 hover:bg-gray-200 dark:hover:bg-gray-800 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            >
              <PanelLeft size={16} />
            </button>
          )}
          <ChatWindow
            key={activeConversation.id}
            employee={employee}
            conversation={activeConversation}
            onSend={sendMessage}
            onClear={clearChat}
            onFeedback={giveFeedback}
          />
        </main>
      </div>
    </div>
  )
}
