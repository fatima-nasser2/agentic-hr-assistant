import { useState, useRef } from 'react'
import { streamMessage, submitFeedback } from '../services/api'
import { v4 as uuidv4 } from 'uuid'

export function useChat() {
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const threadIdRef = useRef(uuidv4())
  const chatHistoryRef = useRef([])

  const sendMessage = async (question) => {
    // Add user message
    const userMessage = {
      id: uuidv4(),
      role: 'user',
      content: question,
      timestamp: new Date()
    }

    // Add placeholder assistant message
    const assistantMessage = {
      id: uuidv4(),
      role: 'assistant',
      content: '',
      question,
      trace: [],
      sources: [],
      retrieval_source: '',
      isStreaming: true,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage, assistantMessage])
    setIsLoading(true)

    const assistantId = assistantMessage.id
    let accumulatedContent = ''

    try {
      await streamMessage(
        question,
        threadIdRef.current,
        chatHistoryRef.current,
        (event) => {
          if (event.type === 'trace') {
            setMessages(prev => prev.map(msg =>
              msg.id === assistantId
                ? { ...msg, trace: [...msg.trace, event] }
                : msg
            ))
          } else if (event.type === 'token') {
            accumulatedContent += event.value
            setMessages(prev => prev.map(msg =>
              msg.id === assistantId
                ? { ...msg, content: msg.content + event.value }
                : msg
            ))
          } else if (event.type === 'done') {
            setMessages(prev => prev.map(msg =>
              msg.id === assistantId
                ? {
                    ...msg,
                    isStreaming: false,
                    sources: event.sources || [],
                    retrieval_source: event.retrieval_source || ''
                  }
                : msg
            ))

            chatHistoryRef.current = [
              ...chatHistoryRef.current,
              { role: 'user', content: question },
              { role: 'assistant', content: accumulatedContent }
            ]
          }
        }
      )
    } catch (err) {
      setMessages(prev => prev.map(msg =>
        msg.id === assistantId
          ? {
              ...msg,
              content: 'Something went wrong. Please try again.',
              isStreaming: false
            }
          : msg
      ))
    } finally {
      setIsLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([])
    threadIdRef.current = uuidv4()
    chatHistoryRef.current = []
  }

  const giveFeedback = async (message, rating) => {
    try {
      await submitFeedback(
        threadIdRef.current,
        message.question,
        message.content,
        rating
      )
    } catch (err) {
      console.error('Feedback error:', err)
    }
  }

  return { messages, isLoading, sendMessage, clearChat, giveFeedback }
}