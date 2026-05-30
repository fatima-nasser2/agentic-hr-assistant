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
        ? 'Recognized as a work-related question — proceeding to find an answer'
        : 'This question is outside the HR assistant scope'
    case 'source_router':
      if (decision === 'faiss') return 'Looking in the HR policy documents'
      if (decision === 'sql') return 'Looking up your personal employee record'
      if (decision === 'internal_kb') return 'Searching the company knowledge base'
      if (decision === 'web') return 'Searching the web for current information'
      return 'Selecting the best data source'
    case 'rag':
      if (details && details.includes('attempt #')) {
        const attempt = details.replace('attempt #', '')
        return attempt === '1'
          ? `Searching for relevant policy sections`
          : `First search wasn't specific enough — trying again with different keywords`
      }
      return 'Searching for relevant documents'
    case 'sql':
      return 'Retrieving your personal data from the employee database'
    case 'internal_kb':
      return 'Searching company announcements, team info, and guidelines'
    case 'grader':
      return decision === 'relevant'
        ? 'Found relevant information — good to answer'
        : 'Information not specific enough — will try again'
    case 'response':
      return 'Composing your answer with citations'
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
        <div className="mt-2 pl-3 border-l-2 border-gray-200 dark:border-gray-700 space-y-2">
          {trace.map((step, i) => (
            <div key={i} className="flex flex-col gap-0.5">
              <span className={clsx(
                'text-xs font-medium',
                NODE_COLORS[step.node] || 'text-gray-500'
              )}>
                {NODE_LABELS[step.node] || step.node}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                {humanizeTrace(step.node, step.decision, step.details)}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}