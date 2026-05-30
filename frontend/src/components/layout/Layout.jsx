import { useState, useEffect } from 'react'
import { PanelLeft } from 'lucide-react'
import clsx from 'clsx'
import Header from './Header'
import Sidebar from './Sidebar'
import ChatWindow from '../chat/ChatWindow'
import { useConversations } from '../../hooks/useConversations'
import { useMediaQuery } from '../../hooks/useMediaQuery'

export default function Layout({ employee, darkMode, onToggleDark, onLogout }) {
  const isMobile = useMediaQuery('(max-width: 767px)')
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile)

  // Sync sidebar state when viewport crosses the breakpoint
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
    giveFeedback,
  } = useConversations()

  const handleSwitch = (id) => {
    switchConversation(id)
    if (isMobile) setSidebarOpen(false)
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-950">
      <Header
        employee={employee}
        darkMode={darkMode}
        onToggleDark={onToggleDark}
        onLogout={onLogout}
      />

      <div className="flex-1 flex overflow-hidden relative">

        {/* Mobile backdrop — tap to close */}
        {isMobile && sidebarOpen && (
          <div
            className="absolute inset-0 z-40 bg-black/40"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Sidebar wrapper
            Desktop: in-flow div that animates its width (pushes chat)
            Mobile:  absolute overlay that slides in via transform        */}
        <div
          className={clsx(
            isMobile
              ? clsx(
                  'absolute left-0 top-0 h-full z-50 transition-transform duration-200',
                  sidebarOpen ? 'translate-x-0' : '-translate-x-full'
                )
              : 'shrink-0 overflow-hidden transition-[width] duration-200'
          )}
          style={!isMobile ? { width: sidebarOpen ? 240 : 0 } : undefined}
        >
          <Sidebar
            conversations={conversations}
            activeId={activeId}
            onNew={newConversation}
            onSwitch={handleSwitch}
            onCollapse={() => setSidebarOpen(false)}
          />
        </div>

        <main className="flex-1 overflow-hidden relative">
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
