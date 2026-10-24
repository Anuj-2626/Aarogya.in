import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

import type { User } from '@/types/auth'
import { authService } from '@/services/authService'

interface AuthContextValue {
  user: User | null
  accessToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (user: User, accessToken: string) => void
  logout: () => Promise<void>
}

interface AuthProviderProps {
  children: ReactNode
}

const AuthContext = createContext<AuthContextValue | undefined>(
  undefined,
)

export function AuthProvider({
  children,
}: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [accessToken, setAccessToken] = useState<string | null>(
    () => localStorage.getItem('access_token'),
  )
  const [isLoading, setIsLoading] = useState<boolean>(
    Boolean(localStorage.getItem('access_token')),
  )

  useEffect(() => {
    const token = localStorage.getItem('access_token')

    if (!token) {
      setIsLoading(false)
      return
    }

    let mounted = true

    const restoreSession = async () => {
      try {
        const currentUser = await authService.getCurrentUser()

        if (!mounted) {
          return
        }

        setUser(currentUser)
        setAccessToken(token)
      } catch {
        if (!mounted) {
          return
        }

        localStorage.removeItem('access_token')
        setUser(null)
        setAccessToken(null)
      } finally {
        if (mounted) {
          setIsLoading(false)
        }
      }
    }

    void restoreSession()

    return () => {
      mounted = false
    }
  }, [])

  const login = (
    loggedInUser: User,
    token: string,
  ) => {
    localStorage.setItem('access_token', token)

    setUser(loggedInUser)
    setAccessToken(token)
  }

  const logout = async () => {
    try {
      if (localStorage.getItem('access_token')) {
        await authService.logout()
      }
    } catch {
      // Local logout must still succeed if the backend request fails.
    } finally {
      localStorage.removeItem('access_token')
      setUser(null)
      setAccessToken(null)
    }
  }

  const value = useMemo(
    () => ({
      user,
      accessToken,
      isAuthenticated: Boolean(accessToken && user),
      isLoading,
      login,
      logout,
    }),
    [user, accessToken, isLoading],
  )

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error(
      'useAuth must be used within an AuthProvider',
    )
  }

  return context
}