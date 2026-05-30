import { useState } from 'react'
import { streamMessage, submitFeedback } from '../services/api'
import { v4 as uuidv4 } from 'uuid'

function createConversation() {
  return {
    id: uuidv4(),
    title: 'New conversation',
    messages: [],
    threadId: uuidv4(),
    chatHistory: [],
    isLoading: false,
  }
}

function truncate(text, max = 40) {
  return text.length > max ? text.slice(0, max) + '…' : text
}

export function useConversations() {
  const initial = createConversation()
  const [conversations, setConversations] = useState([initial])
  const [activeId, setActiveId] = useState(initial.id)

  const activeConversation =
    conversations.find(c => c.id === activeId) ?? conversations[0]

  const newConversation = () => {
    const conv = createConversation()
    setConversations(prev => [conv, ...prev])
    setActiveId(conv.id)
  }

  const switchConversation = (id) => setActiveId(id)

  const sendMessage = async (question) => {
    // Capture stable references before any async work
    const convId = activeId
    const conv = conversations.find(c => c.id === convId)
    const { threadId, chatHistory, messages } = conv

    const userMsg = {
      id: uuidv4(),
      role: 'user',
      content: question,
      timestamp: new Date(),
    }
    const assistantMsg = {
      id: uuidv4(),
      role: 'assistant',
      content: '',
      question,
      trace: [],
      sources: [],
      retrieval_source: '',
      isStreaming: true,
      timestamp: new Date(),
    }
    const assistantId = assistantMsg.id
    const title = messages.length === 0 ? truncate(question) : conv.title

    setConversations(prev => {
      const updated = prev.map(c =>
        c.id === convId
          ? { ...c, title, isLoading: true, messages: [...c.messages, userMsg, assistantMsg] }
          : c
      )
      // Bubble the active conversation to the top
      const idx = updated.findIndex(c => c.id === convId)
      if (idx > 0) {
        const [target] = updated.splice(idx, 1)
        updated.unshift(target)
      }
      return updated
    })

    let accumulatedContent = ''

    try {
      await streamMessage(question, threadId, chatHistory, (event) => {
        if (event.type === 'trace') {
          setConversations(prev => prev.map(c =>
            c.id === convId
              ? { ...c, messages: c.messages.map(m => m.id === assistantId ? { ...m, trace: [...m.trace, event] } : m) }
              : c
          ))
        } else if (event.type === 'token') {
          accumulatedContent += event.value
          setConversations(prev => prev.map(c =>
            c.id === convId
              ? { ...c, messages: c.messages.map(m => m.id === assistantId ? { ...m, content: m.content + event.value } : m) }
              : c
          ))
        } else if (event.type === 'done') {
          setConversations(prev => prev.map(c =>
            c.id === convId
              ? {
                  ...c,
                  isLoading: false,
                  chatHistory: [
                    ...c.chatHistory,
                    { role: 'user', content: question },
                    { role: 'assistant', content: accumulatedContent },
                  ],
                  messages: c.messages.map(m =>
                    m.id === assistantId
                      ? {
                          ...m,
                          isStreaming: false,
                          sources: event.sources || [],
                          retrieval_source: event.retrieval_source || '',
                          evaluation: event.evaluation || null,
                        }
                      : m
                  ),
                }
              : c
          ))
        }
      })
    } catch {
      setConversations(prev => prev.map(c =>
        c.id === convId
          ? {
              ...c,
              isLoading: false,
              messages: c.messages.map(m =>
                m.id === assistantId
                  ? { ...m, content: 'Something went wrong. Please try again.', isStreaming: false }
                  : m
              ),
            }
          : c
      ))
    }
  }

  const clearChat = () => {
    setConversations(prev => prev.map(c =>
      c.id === activeId
        ? { ...c, title: 'New conversation', messages: [], chatHistory: [], threadId: uuidv4() }
        : c
    ))
  }

  const renameConversation = (id, title) => {
    setConversations(prev => prev.map(c =>
      c.id === id ? { ...c, title: title.trim() || c.title } : c
    ))
  }

  const deleteConversation = (id) => {
    setConversations(prev => {
      const next = prev.filter(c => c.id !== id)
      if (next.length === 0) {
        const fresh = createConversation()
        setActiveId(fresh.id)
        return [fresh]
      }
      if (id === activeId) {
        setActiveId(next[0].id)
      }
      return next
    })
  }

  const giveFeedback = async (message, rating) => {
    const conv = conversations.find(c => c.id === activeId)
    const evalId = message.evaluation?.eval_id ?? null
    try {
      await submitFeedback(conv.threadId, message.question, message.content, rating, undefined, evalId)
    } catch (err) {
      console.error('Feedback error:', err)
    }
  }

  return {
    conversations,
    activeId,
    activeConversation,
    newConversation,
    switchConversation,
    sendMessage,
    clearChat,
    renameConversation,
    deleteConversation,
    giveFeedback,
  }
}
