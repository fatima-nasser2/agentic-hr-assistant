import { useState, useRef, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { Plus, MessageSquare, PanelLeftClose, LogOut, MoreHorizontal, MoreVertical, Pencil, Trash2 } from 'lucide-react'
import clsx from 'clsx'

/* ── Profile section ─────────────────────────────────────────────────── */

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
        <div className="w-7 h-7 rounded-full bg-brand-500 flex items-center justify-center text-white text-xs font-bold shrink-0">
          {employee.name?.charAt(0)}
        </div>
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

/* ── Conversation item with three-dots menu ──────────────────────────── */

function ConversationItem({ conv, isActive, onSwitch, onRename, onDelete }) {
  const [menuAnchor, setMenuAnchor] = useState(null) // { top, left, width } when open
  const [renaming, setRenaming] = useState(false)
  const [draft, setDraft] = useState('')
  const inputRef = useRef(null)
  const btnRef = useRef(null)

  useEffect(() => {
    if (renaming) inputRef.current?.select()
  }, [renaming])

  const openMenu = (e) => {
    e.stopPropagation()
    const rect = btnRef.current.getBoundingClientRect()
    setMenuAnchor({ top: rect.bottom + 4, left: rect.left, width: 160 })
  }

  const closeMenu = () => setMenuAnchor(null)

  const startRename = () => {
    setDraft(conv.title)
    setRenaming(true)
    closeMenu()
  }

  const commitRename = () => {
    if (draft.trim()) onRename(conv.id, draft.trim())
    setRenaming(false)
  }

  const handleRenameKey = (e) => {
    if (e.key === 'Enter') commitRename()
    if (e.key === 'Escape') setRenaming(false)
  }

  const handleDelete = () => {
    closeMenu()
    onDelete(conv.id)
  }

  return (
    <>
      <div
        role="button"
        tabIndex={0}
        onClick={() => !renaming && onSwitch(conv.id)}
        onKeyDown={(e) => e.key === 'Enter' && !renaming && onSwitch(conv.id)}
        title={renaming ? undefined : conv.title}
        className={clsx(
          'group w-full text-left px-3 py-2.5 rounded-lg transition-colors cursor-pointer flex items-start gap-2.5',
          isActive
            ? 'bg-white dark:bg-gray-800 shadow-sm border border-gray-200 dark:border-gray-700'
            : 'hover:bg-brand-50 dark:hover:bg-brand-500/10 border border-transparent'
        )}
      >
        <MessageSquare
          size={14}
          className={clsx(
            'shrink-0 mt-0.5',
            isActive ? 'text-brand-500' : 'text-gray-400 dark:text-gray-600'
          )}
        />

        <div className="flex-1 min-w-0">
          {renaming ? (
            <input
              ref={inputRef}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onBlur={commitRename}
              onKeyDown={handleRenameKey}
              onClick={(e) => e.stopPropagation()}
              className="w-full text-sm font-medium bg-transparent border-b border-brand-400 outline-none text-gray-900 dark:text-white"
            />
          ) : (
            <span className={clsx(
              'text-sm font-medium leading-snug line-clamp-2',
              isActive ? 'text-gray-900 dark:text-white' : 'text-gray-600 dark:text-gray-400'
            )}>
              {conv.title}
            </span>
          )}
          {conv.isLoading && (
            <p className="text-xs text-brand-400 mt-1">Thinking…</p>
          )}
        </div>

        {/* Three-dots button — visible on hover or when menu is open */}
        {!renaming && (
          <button
            ref={btnRef}
            onClick={openMenu}
            aria-label="Conversation options"
            className={clsx(
              'shrink-0 p-0.5 rounded transition-opacity',
              menuAnchor
                ? 'opacity-100 text-gray-500 dark:text-gray-400'
                : 'opacity-0 group-hover:opacity-100 text-gray-400 dark:text-gray-600 hover:text-gray-600 dark:hover:text-gray-400'
            )}
          >
            <MoreVertical size={13} />
          </button>
        )}
      </div>

      {/* Portal dropdown menu */}
      {menuAnchor && createPortal(
        <>
          {/* Backdrop — full screen, closes menu on click */}
          <div
            className="fixed inset-0 z-40"
            onClick={closeMenu}
          />

          {/* Menu */}
          <div
            className="fixed z-50 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-xl overflow-hidden py-1"
            style={{ top: menuAnchor.top, left: menuAnchor.left, width: menuAnchor.width }}
          >
            <button
              onClick={startRename}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/60 transition-colors"
            >
              <Pencil size={13} className="text-gray-400 dark:text-gray-500" />
              Rename
            </button>
            <div className="my-1 border-t border-gray-100 dark:border-gray-700" />
            <button
              onClick={handleDelete}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
            >
              <Trash2 size={13} />
              Delete
            </button>
          </div>
        </>,
        document.body
      )}
    </>
  )
}

/* ── Sidebar ─────────────────────────────────────────────────────────── */

export default function Sidebar({ conversations, activeId, onNew, onSwitch, onCollapse, onRename, onDelete, isMobile, employee, onLogout }) {
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
          <ConversationItem
            key={conv.id}
            conv={conv}
            isActive={conv.id === activeId}
            onSwitch={onSwitch}
            onRename={onRename}
            onDelete={onDelete}
          />
        ))}
      </nav>

      {/* Profile at bottom */}
      <ProfileSection employee={employee} onLogout={onLogout} />
    </aside>
  )
}
