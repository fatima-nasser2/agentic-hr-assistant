import { useEffect, useRef } from 'react'
import { Trash2, Bot } from 'lucide-react'
import ChatMessage from './ChatMessage'
import ChatInput from './ChatInput'

export default function ChatWindow({ employee, conversation, onSend, onClear, onFeedback }) {
  const { messages, isLoading } = conversation
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="h-full flex flex-col max-w-3xl mx-auto px-4">

      {/* Messages */}
      <div className="flex-1 overflow-y-auto py-6 space-y-6 scrollbar-hidden">

        {/* Welcome state */}
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center gap-4 pb-20">
            <div className="w-12 h-12 rounded-2xl bg-brand-500 flex items-center justify-center shadow-lg">
              <Bot size={24} className="text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Hi {employee?.name?.split(' ')[0]} 👋
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 max-w-sm">
                Ask me anything about HR policies, your leave balance, or company information.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-2 mt-2 w-full max-w-sm">
              {[
                'How many sick days do I have left?',
                'What is the parental leave policy?',
                'Who is the CTO of NovaTech?',
                'When is my next performance review?',
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => onSend(suggestion)}
                  className="text-xs text-left px-3 py-2.5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-600 dark:text-gray-400 hover:border-brand-500 hover:text-brand-500 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Chat messages */}
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message}
            onFeedback={onFeedback}
          />
        ))}

        <div ref={bottomRef} />
      </div>

      {/* Input area */}
      <div className="py-4 border-t border-gray-100 dark:border-gray-800">
        <div className="flex items-center justify-between mb-3">
          {messages.length > 0 && (
            <button
              onClick={onClear}
              className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            >
              <Trash2 size={12} />
              Clear chat
            </button>
          )}
        </div>
        <ChatInput onSend={onSend} disabled={isLoading} />
        <p className="text-xs text-center text-gray-300 dark:text-gray-700 mt-2">
          NovaTech HR Assistant · Powered by Agentic RAG
        </p>
      </div>
    </div>
  )
}
