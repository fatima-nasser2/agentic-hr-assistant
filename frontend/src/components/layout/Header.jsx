import { Sun, Moon, Bot } from 'lucide-react'

export default function Header({ darkMode, onToggleDark }) {
  return (
    <header className="h-14 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 flex items-center justify-between px-6 shrink-0">

      {/* Logo */}
      <div className="flex items-center gap-2.5">
        <div className="w-7 h-7 rounded-lg bg-brand-500 flex items-center justify-center">
          <Bot size={16} className="text-white" />
        </div>
        <span className="font-semibold text-gray-900 dark:text-white text-sm">
          NovaTech HR Assistant
        </span>
      </div>

      {/* Dark mode toggle */}
      <button
        onClick={onToggleDark}
        aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
        className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      >
        {darkMode ? <Sun size={16} /> : <Moon size={16} />}
      </button>
    </header>
  )
}
