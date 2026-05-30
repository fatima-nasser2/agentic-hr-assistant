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

function humanizeTrace(node, decision, details) {
  switch (node) {
    case 'router':
      return decision === 'rag'
        ? 'Recognised as an HR question — searching for an answer'
        : 'This question is outside the HR assistant scope'

    case 'source_router':
      if (decision === 'faiss')      return 'Searching HR policy documents'
      if (decision === 'sql')        return 'Looking up your employee record'
      if (decision === 'internal_kb') return 'Searching the company knowledge base'
      if (decision === 'web')        return 'Searching the web for current information'
      return 'Selecting the best data source'

    case 'rag': {
      // decision = "attempt #1", "attempt #2", …
      // details  = the actual (rewritten) question sent to the retriever
      const attempt = parseInt(decision?.match(/#(\d+)/)?.[1] ?? '1', 10)
      if (attempt === 1) {
        return details ? `Searching for: "${details}"` : 'Searching for relevant documents'
      }
      return details
        ? `Refining search — trying: "${details}"`
        : 'Refining search with different keywords'
    }

    case 'sql':
      // details = "Retrieved data for <employee_id>"
      return details || 'Querying the employee database'

    case 'internal_kb':
      return 'Searching company knowledge base'

    case 'grader':
      return decision === 'relevant'
        ? 'Found relevant information — proceeding to answer'
        : 'Information not specific enough — searching again'

    case 'response':
      return 'Composing your answer'

    case 'unknown':
      return 'This question is outside what I can help with'

    default:
      return details || decision || ''
  }
}

export default function AgentTrace({ trace, isStreaming }) {
  const [expanded, setExpanded] = useState(false)

  if (!trace || trace.length === 0) return null

  return (
    <div className="mb-3">
      {/* Toggle button */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1.5 text-sm text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
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
        <div className="mt-2 pl-3 border-l-2 border-gray-200 dark:border-gray-700 space-y-2">
          {trace.map((step, i) => (
            <div key={i} className="flex flex-col gap-0.5">
              <span className={clsx(
                'text-sm font-medium',
                NODE_COLORS[step.node] || 'text-gray-500'
              )}>
                {NODE_LABELS[step.node] || step.node}
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
                {humanizeTrace(step.node, step.decision, step.details)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}