import { useState, useRef, useEffect } from 'react'
import { Plus, MessageSquare, PanelLeftClose, LogOut, MoreHorizontal } from 'lucide-react'
import clsx from 'clsx'

function ProfileSection({ employee, onLogout }) {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    if (!open) return
    const handleClick = (e) => {
      if (!ref.current?.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [open])

  if (!employee) return null

  return (
    <div ref={ref} className="relative p-2 border-t border-gray-100 dark:border-gray-800">

      {/* Popup menu — opens upward */}
      {open && (
        <div className="absolute bottom-full left-2 right-2 mb-1.5 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-lg overflow-hidden">
          <div className="px-3 py-3">
            <p className="text-sm font-semibold text-gray-900 dark:text-white leading-tight">
              {employee.name}
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
              {employee.id}
            </p>
          </div>
          <div className="border-t border-gray-100 dark:border-gray-700">
            <button
              onClick={() => { setOpen(false); onLogout() }}
              className="w-full flex items-center gap-2.5 px-3 py-2.5 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
            >
              <LogOut size={14} />
              Log out
            </button>
          </div>
        </div>
      )}

      {/* Profile button */}
      <button
        onClick={() => setOpen(prev => !prev)}
        aria-label="Profile menu"
        aria-expanded={open}
        className={clsx(
          'w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg transition-colors',
          open
            ? 'bg-gray-100 dark:bg-gray-800'
            : 'hover:bg-gray-100 dark:hover:bg-gray-800'
        )}
      >
        {/* Avatar */}
        <div className="w-7 h-7 rounded-full bg-brand-500 flex items-center justify-center text-white text-xs font-bold shrink-0">
          {employee.name?.charAt(0)}
        </div>

        {/* Name + ID */}
        <div className="flex-1 min-w-0 text-left">
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate leading-tight">
            {employee.name}
          </p>
          <p className="text-xs text-gray-400 dark:text-gray-500 leading-tight">
            {employee.id}
          </p>
        </div>

        <MoreHorizontal size={14} className="text-gray-400 dark:text-gray-600 shrink-0" />
      </button>
    </div>
  )
}

export default function Sidebar({ conversations, activeId, onNew, onSwitch, onCollapse, isMobile, employee, onLogout }) {
  return (
    <aside className={clsx(
      'h-full flex flex-col bg-white dark:bg-gray-900',
      isMobile ? 'w-72' : 'w-full'
    )}>

      {/* Header */}
      <div className="px-3 pt-3 pb-2 flex items-center gap-2">
        <button
          onClick={onNew}
          aria-label="New conversation"
          className="flex-1 flex items-center gap-2 px-3 py-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-750 shadow-sm transition-colors"
        >
          <Plus size={14} className="shrink-0 text-brand-500" />
          New conversation
        </button>
        <button
          onClick={onCollapse}
          aria-label="Collapse sidebar"
          className="p-2 rounded-lg text-gray-400 dark:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-600 dark:hover:text-gray-300 transition-colors shrink-0"
        >
          <PanelLeftClose size={15} />
        </button>
      </div>

      {/* Section label */}
      <div className="px-4 pt-2 pb-1.5">
        <span className="text-xs font-semibold text-gray-400 dark:text-gray-600 uppercase tracking-wider">
          This session
        </span>
      </div>

      {/* Conversation list */}
      <nav className="flex-1 overflow-y-auto scrollbar-hidden px-2 pb-2 space-y-0.5">
        {conversations.map(conv => (
          <button
            key={conv.id}
            onClick={() => onSwitch(conv.id)}
            title={conv.title}
            className={clsx(
              'w-full text-left px-3 py-2.5 rounded-lg transition-colors',
              conv.id === activeId
                ? 'bg-white dark:bg-gray-800 shadow-sm border border-gray-200 dark:border-gray-700'
                : 'hover:bg-white/80 dark:hover:bg-gray-800/60 border border-transparent'
            )}
          >
            <div className="flex items-start gap-2.5">
              <MessageSquare
                size={14}
                className={clsx(
                  'shrink-0 mt-0.5',
                  conv.id === activeId ? 'text-brand-500' : 'text-gray-400 dark:text-gray-600'
                )}
              />
              <span className={clsx(
                'text-sm font-medium leading-snug line-clamp-2 text-left',
                conv.id === activeId ? 'text-gray-900 dark:text-white' : 'text-gray-600 dark:text-gray-400'
              )}>
                {conv.title}
              </span>
            </div>
            {conv.isLoading && (
              <p className="text-xs text-brand-400 mt-1 ml-6">Thinking…</p>
            )}
          </button>
        ))}
      </nav>

      {/* Profile at bottom */}
      <ProfileSection employee={employee} onLogout={onLogout} />
    </aside>
  )
}
