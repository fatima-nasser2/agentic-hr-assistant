import Header from './Header'
import ChatWindow from '../chat/ChatWindow'

export default function Layout({ employee, token, darkMode, onToggleDark, onLogout }) {
  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-950">
      <Header
        employee={employee}
        darkMode={darkMode}
        onToggleDark={onToggleDark}
        onLogout={onLogout}
      />
      <main className="flex-1 overflow-hidden">
        <ChatWindow employee={employee} />
      </main>
    </div>
  )
}