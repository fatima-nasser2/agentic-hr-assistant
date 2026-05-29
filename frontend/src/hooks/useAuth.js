import { useState } from 'react'
import { login } from '../services/api'

export function useAuth() {
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [employee, setEmployee] = useState(
    JSON.parse(localStorage.getItem('employee') || 'null')
  )
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleLogin = async (employeeId) => {
    setLoading(true)
    setError(null)
    try {
      const data = await login(employeeId)
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('employee', JSON.stringify({
        id: data.employee_id,
        name: data.name
      }))
      setToken(data.access_token)
      setEmployee({ id: data.employee_id, name: data.name })
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please check your employee ID.')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('employee')
    setToken(null)
    setEmployee(null)
  }

  return { token, employee, loading, error, handleLogin, handleLogout }
}