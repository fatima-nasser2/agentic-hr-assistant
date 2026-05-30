import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE,
})

// Attach token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid — clear storage and reload
      localStorage.removeItem('token')
      localStorage.removeItem('employee')
      window.location.href = '/'
    }
    return Promise.reject(error)
  }
)

// ── AUTH ─────────────────────────────────────────────────

export const login = async (employeeId) => {
  const response = await api.post('/auth/login', { employee_id: employeeId })
  return response.data
}

// ── CHAT ─────────────────────────────────────────────────

export const sendMessage = async (question, threadId, chatHistory) => {
  const response = await api.post('/chat', {
    question,
    thread_id: threadId,
    chat_history: chatHistory
  })
  return response.data
}

export const streamMessage = async (question, threadId, chatHistory, onEvent) => {
  const token = localStorage.getItem('token')

  const response = await fetch(`${API_BASE}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      question,
      thread_id: threadId,
      chat_history: chatHistory
    })
  })

  if (response.status === 401) {
    localStorage.removeItem('token')
    localStorage.removeItem('employee')
    window.location.href = '/'
    return
  }

  if (!response.ok) {
    throw new Error(`Stream request failed: ${response.status} ${response.statusText}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    const chunk = decoder.decode(value)
    const lines = chunk.split('\n')

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6))
          onEvent(data)
        } catch (e) {
          // skip malformed lines
        }
      }
    }
  }
}

// ── FEEDBACK ─────────────────────────────────────────────

export const submitFeedback = async (threadId, question, answer, rating, comment, evalId) => {
  const response = await api.post('/feedback', {
    thread_id: threadId,
    question,
    answer,
    rating,
    comment,
    eval_id: evalId || null,
  })
  return response.data
}

// ── SOURCES ──────────────────────────────────────────────

export const getSources = async () => {
  const response = await api.get('/sources')
  return response.data
}