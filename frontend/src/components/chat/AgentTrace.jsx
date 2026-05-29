import { useState } from 'react'
import { ChevronDown, ChevronRight, Brain } from 'lucide-react'
import clsx from 'clsx'

const NODE_LABELS = {
  router: 'Router Agent',
  source_router: 'Source Router',
  rag: 'RAG Agent',
  sql: 'SQL Agent',
  internal_kb: 'Internal KB Agent',
  grader: 'Grader Agent',
  response: 'Response Agent',
  unknown: 'Unknown Node'
}

const NODE_COLORS = {
  router: 'text-violet-500',
  source_router: 'text-blue-500',
  rag: 'text-teal-500',
  sql: 'text-orange-500',
  internal_kb: 'text-cyan-500',
  grader: 'text-amber-500',
  response: 'text-green-500',
  unknown: 'text-red-500'
}

export default function AgentTrace({ trace, isStreaming }) {
  const [expanded, setExpanded] = useState(false)

  if (!trace || trace.length === 0) return null

  return (
    <div className="mb-3">
      {/* Toggle button */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1.5 text-xs text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
      >
        <Brain size={12} />
        <span>
          {isStreaming ? 'Thinking...' : `${trace.length} steps`}
        </span>
        {isStreaming ? (
          <span className="flex gap-0.5 ml-1">
            <span className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </span>
        ) : (
          expanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />
        )}
      </button>

      {/* Expanded trace */}
      {expanded && !isStreaming && (
        <div className="mt-2 pl-3 border-l-2 border-gray-200 dark:border-gray-700 space-y-1.5">
          {trace.map((step, i) => (
            <div key={`${step.node}-${i}`} className="flex items-start gap-2">
              <span className={clsx('text-xs font-medium shrink-0', NODE_COLORS[step.node] || 'text-gray-500')}>
                {NODE_LABELS[step.node] || step.node}
              </span>
              {step.decision && (
                <span className="text-xs text-gray-400 dark:text-gray-500">
                  → {step.decision}
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}