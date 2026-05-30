import { Plus, MessageSquare, PanelLeftClose } from 'lucide-react'
import clsx from 'clsx'

export default function Sidebar({ conversations, activeId, onNew, onSwitch, onCollapse }) {
  return (
    <aside className="h-full w-60 shrink-0 flex flex-col bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800">

      {/* Header row */}
      <div className="p-3 flex items-center gap-2">
        <button
          onClick={onNew}
          aria-label="New conversation"
          className="flex-1 flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        >
          <Plus size={15} className="shrink-0" />
          New conversation
        </button>
        <button
          onClick={onCollapse}
          aria-label="Collapse sidebar"
          className="p-2 rounded-xl text-gray-400 dark:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-600 dark:hover:text-gray-300 transition-colors shrink-0"
        >
          <PanelLeftClose size={15} />
        </button>
      </div>

      <div className="px-3 pb-2">
        <span className="text-xs font-medium text-gray-400 dark:text-gray-600 uppercase tracking-wide">
          This session
        </span>
      </div>

      {/* Conversation list */}
      <nav className="flex-1 overflow-y-auto scrollbar-hidden px-2 pb-4 space-y-0.5">
        {conversations.map(conv => (
          <button
            key={conv.id}
            onClick={() => onSwitch(conv.id)}
            className={clsx(
              'w-full text-left px-3 py-2.5 rounded-xl transition-colors group',
              conv.id === activeId
                ? 'bg-brand-50 dark:bg-brand-500/10'
                : 'hover:bg-gray-100 dark:hover:bg-gray-800'
            )}
          >
            <div className="flex items-center gap-2">
              <MessageSquare
                size={13}
                className={clsx(
                  'shrink-0',
                  conv.id === activeId
                    ? 'text-brand-500'
                    : 'text-gray-400 dark:text-gray-600'
                )}
              />
              <span className={clsx(
                'text-sm font-medium truncate',
                conv.id === activeId
                  ? 'text-brand-600 dark:text-brand-400'
                  : 'text-gray-600 dark:text-gray-400'
              )}>
                {conv.title}
              </span>
            </div>
            {conv.isLoading && (
              <p className="text-sm text-brand-400 mt-0.5 ml-5">Thinking…</p>
            )}
          </button>
        ))}
      </nav>
    </aside>
  )
}
