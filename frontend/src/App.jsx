import LoginScreen from './components/auth/LoginScreen'
import Layout from './components/layout/Layout'
import { useAuth } from './hooks/useAuth'
import { useTheme } from './hooks/useTheme'

function App() {
  const { token, employee, loading, error, handleLogin, handleLogout } = useAuth()
  const { darkMode, toggleDark } = useTheme()

  if (!token) {
    return (
      <LoginScreen
        onLogin={handleLogin}
        loading={loading}
        error={error}
        darkMode={darkMode}
        onToggleDark={toggleDark}
      />
    )
  }

  return (
    <Layout
      employee={employee}
      token={token}
      darkMode={darkMode}
      onToggleDark={toggleDark}
      onLogout={handleLogout}
    />
  )
}

export default App