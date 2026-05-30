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
      if (decision === 'faiss')       return 'Searching HR policy documents'
      if (decision === 'sql')         return 'Looking up your employee record'
      if (decision === 'internal_kb') return 'Searching the company knowledge base'
      if (decision === 'web')         return 'Searching the web for current information'
      return 'Selecting the best data source'

    case 'rag': {
      const attempt = parseInt(decision?.match(/#(\d+)/)?.[1] ?? '1', 10)
      if (attempt === 1) {
        return details ? `Searching for: "${details}"` : 'Searching for relevant documents'
      }
      return details
        ? `Refining search — trying: "${details}"`
        : 'Refining search with different keywords'
    }

    case 'sql':
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

// ── Score helpers ────────────────────────────────────────

function scoreColor(score) {
  if (score >= 4.0) return { dot: 'bg-green-500', bar: 'bg-green-500', text: 'text-green-600 dark:text-green-400', badge: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300' }
  if (score >= 2.5) return { dot: 'bg-amber-400', bar: 'bg-amber-400', text: 'text-amber-600 dark:text-amber-400', badge: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300' }
  return { dot: 'bg-red-500', bar: 'bg-red-500', text: 'text-red-600 dark:text-red-400', badge: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300' }
}

function ScoreBar({ label, score }) {
  const pct = Math.round((score / 5) * 100)
  const colors = scoreColor(score)
  return (
    <div className="flex items-center gap-2">
      <span className="w-24 shrink-0 text-xs text-gray-500 dark:text-gray-400">{label}</span>
      <div className="flex-1 h-1.5 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          className={clsx('h-full rounded-full transition-all duration-500', colors.bar)}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className={clsx('w-7 shrink-0 text-right text-xs font-medium', colors.text)}>
        {score.toFixed(1)}
      </span>
    </div>
  )
}

// ── Main component ───────────────────────────────────────

export default function AgentTrace({ trace, isStreaming, evaluation }) {
  const [expanded, setExpanded] = useState(false)

  if (!trace || trace.length === 0) return null

  const overallColors = evaluation ? scoreColor(evaluation.overall) : null

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
          <>
            {/* Inline quality indicator when collapsed */}
            {evaluation && !expanded && (
              <span className={clsx('ml-1 flex items-center gap-1 text-xs font-medium px-1.5 py-0.5 rounded-full', overallColors.badge)}>
                <span className={clsx('w-1.5 h-1.5 rounded-full', overallColors.dot)} />
                {evaluation.overall.toFixed(1)}
              </span>
            )}
            {expanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
          </>
        )}
      </button>

      {/* Expanded panel */}
      {expanded && !isStreaming && (
        <div className="mt-2 pl-3 border-l-2 border-gray-200 dark:border-gray-700 space-y-2">
          {/* Trace steps */}
          {trace.map((step, i) => (
            <div key={i} className="flex flex-col gap-0.5">
              <span className={clsx('text-sm font-medium', NODE_COLORS[step.node] || 'text-gray-500')}>
                {NODE_LABELS[step.node] || step.node}
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
                {humanizeTrace(step.node, step.decision, step.details)}
              </span>
            </div>
          ))}

          {/* Quality scores */}
          {evaluation && (
            <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700/60 space-y-2">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wide">
                  Answer Quality
                </span>
                <span className={clsx('text-xs font-bold px-2 py-0.5 rounded-full', overallColors.badge)}>
                  {evaluation.overall.toFixed(1)} / 5
                </span>
              </div>

              <ScoreBar label="Groundedness" score={evaluation.groundedness} />
              <ScoreBar label="Relevance"    score={evaluation.relevance} />
              <ScoreBar label="Completeness" score={evaluation.completeness} />

              {evaluation.reasoning && (
                <p className="text-xs italic text-gray-400 dark:text-gray-500 leading-relaxed pt-1">
                  {evaluation.reasoning}
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
