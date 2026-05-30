import { useState } from 'react'
import { PanelLeft } from 'lucide-react'
import Header from './Header'
import Sidebar from './Sidebar'
import ChatWindow from '../chat/ChatWindow'
import { useConversations } from '../../hooks/useConversations'

export default function Layout({ employee, darkMode, onToggleDark, onLogout }) {
  const [sidebarOpen, setSidebarOpen] = useState(true)

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

  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-950">
      <Header
        employee={employee}
        darkMode={darkMode}
        onToggleDark={onToggleDark}
        onLogout={onLogout}
      />
      <div className="flex-1 flex overflow-hidden">

        {/* Sidebar — animate width so the chat area slides smoothly */}
        <div
          className="shrink-0 overflow-hidden transition-[width] duration-200"
          style={{ width: sidebarOpen ? 240 : 0 }}
        >
          <Sidebar
            conversations={conversations}
            activeId={activeId}
            onNew={newConversation}
            onSwitch={switchConversation}
            onCollapse={() => setSidebarOpen(false)}
          />
        </div>

        <main className="flex-1 overflow-hidden relative">
          {/* Expand button — visible only when sidebar is closed */}
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
