import { Sun, Moon, LogOut, Bot } from 'lucide-react'

export default function Header({ employee, darkMode, onToggleDark, onLogout }) {
  return (
    <header className="h-14 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 flex items-center justify-between px-6 shrink-0">

      {/* Left — Logo */}
      <div className="flex items-center gap-2.5">
        <div className="w-7 h-7 rounded-lg bg-brand-500 flex items-center justify-center">
          <Bot size={16} className="text-white" />
        </div>
        <span className="font-semibold text-gray-900 dark:text-white text-sm">
          NovaTech HR Assistant
        </span>
      </div>

      {/* Right — Controls */}
      <div className="flex items-center gap-3">

        {/* Employee badge */}
        {employee && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-gray-100 dark:bg-gray-800">
            <div className="w-5 h-5 rounded-full bg-brand-500 flex items-center justify-center text-white text-xs font-bold">
              {employee.name?.charAt(0)}
            </div>
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              {employee.name}
            </span>
            <span className="text-xs text-gray-400 dark:text-gray-500">
              {employee.id}
            </span>
          </div>
        )}

        {/* Dark mode toggle */}
        <button
          onClick={onToggleDark}
          aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
          className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          {darkMode ? <Sun size={16} /> : <Moon size={16} />}
        </button>

        {/* Logout */}
        <button
          onClick={onLogout}
          aria-label="Log out"
          className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          <LogOut size={16} />
        </button>
      </div>
    </header>
  )
}