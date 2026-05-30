import { useState } from 'react'
import { ThumbsUp, ThumbsDown, Bot, User } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import AgentTrace from './AgentTrace'
import clsx from 'clsx'

function evalDotColor(overall) {
  if (overall >= 4.0) return 'bg-green-500'
  if (overall >= 2.5) return 'bg-amber-400'
  return 'bg-red-500'
}

export default function ChatMessage({ message, onFeedback }) {
  const [feedback, setFeedback] = useState(null)

  const handleFeedback = (rating) => {
    setFeedback(rating)
    onFeedback(message, rating)
  }

  const isUser = message.role === 'user'
  const hasEval = !isUser && !message.isStreaming && message.evaluation

  return (
    <div className={clsx('flex gap-3 group', isUser && 'flex-row-reverse')}>

      {/* Avatar */}
      <div className="relative shrink-0 mt-0.5">
        <div className={clsx(
          'w-7 h-7 rounded-full flex items-center justify-center',
          isUser
            ? 'bg-brand-500'
            : 'bg-gray-100 dark:bg-gray-800'
        )}>
          {isUser
            ? <User size={14} className="text-white" />
            : <Bot size={14} className="text-gray-500 dark:text-gray-400" />
          }
        </div>
        {/* Quality dot — bottom-right of avatar */}
        {hasEval && (
          <span
            className={clsx(
              'absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-white dark:border-gray-950',
              evalDotColor(message.evaluation.overall)
            )}
          />
        )}
      </div>

      {/* Bubble */}
      <div className={clsx(
        'max-w-[75%] space-y-1',
        isUser ? 'items-end' : 'items-start'
      )}>
        {/* Agent trace — only for assistant */}
        {!isUser && (
          <AgentTrace
            trace={message.trace}
            isStreaming={message.isStreaming}
            evaluation={message.evaluation}
          />
        )}

        {/* Message content */}
        <div className={clsx(
          'px-4 py-3 rounded-2xl text-sm leading-relaxed',
          isUser
            ? 'bg-brand-500 text-white rounded-tr-sm'
            : 'bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 border border-gray-100 dark:border-gray-800 rounded-tl-sm shadow-sm'
        )}>
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <ReactMarkdown
              components={{
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                ul: ({ children }) => <ul className="list-disc list-inside space-y-1 mb-2">{children}</ul>,
                li: ({ children }) => <li>{children}</li>,
              }}
            >
              {message.content || ''}
            </ReactMarkdown>
          )}
        </div>

        {/* Feedback — only for completed assistant messages */}
        {!isUser && !message.isStreaming && message.content && (
          <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity px-1">
            <button
              onClick={() => handleFeedback('up')}
              className={clsx(
                'p-1 rounded-md transition-colors',
                feedback === 'up'
                  ? 'text-green-500'
                  : 'text-gray-300 dark:text-gray-600 hover:text-green-500'
              )}
            >
              <ThumbsUp size={13} />
            </button>
            <button
              onClick={() => handleFeedback('down')}
              className={clsx(
                'p-1 rounded-md transition-colors',
                feedback === 'down'
                  ? 'text-red-500'
                  : 'text-gray-300 dark:text-gray-600 hover:text-red-500'
              )}
            >
              <ThumbsDown size={13} />
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
