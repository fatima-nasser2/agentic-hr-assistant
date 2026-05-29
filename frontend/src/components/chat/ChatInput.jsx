import { useState } from 'react'
import { Send } from 'lucide-react'
import clsx from 'clsx'

export default function ChatInput({ onSend, disabled }) {
  const [value, setValue] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!value.trim() || disabled) return
    onSend(value.trim())
    setValue('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-end gap-3">
      <div className="flex-1 relative">
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about HR policies, your leave balance, company info..."
          rows={1}
          disabled={disabled}
          className="w-full resize-none px-4 py-3 pr-12 rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900 dark:text-white placeholder-gray-400 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent disabled:opacity-50 max-h-32 overflow-y-auto"
          style={{ minHeight: '48px' }}
        />
      </div>
      <button
        type="submit"
        aria-label="Send message"
        disabled={!value.trim() || disabled}
        className={clsx(
          'w-10 h-10 rounded-xl flex items-center justify-center transition-colors shrink-0',
          value.trim() && !disabled
            ? 'bg-brand-500 hover:bg-brand-600 text-white'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-400 cursor-not-allowed'
        )}
      >
        <Send size={16} />
      </button>
    </form>
  )
}