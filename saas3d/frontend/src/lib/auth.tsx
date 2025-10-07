'use client'

import { useState, useEffect, createContext, useContext, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { auth, User } from '@/lib/api'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>
  register: (email: string, password: string) => Promise<{ success: boolean; error?: string }>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    if (!auth.isAuthenticated()) {
      setIsLoading(false)
      return
    }

    try {
      const response = await auth.getCurrentUser()
      if (response.data) {
        setUser(response.data)
      } else {
        auth.logout()
      }
    } catch (error) {
      auth.logout()
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    try {
      const response = await auth.login({ email, password })
      if (response.data) {
        await checkAuth()
        return { success: true }
      } else {
        return { success: false, error: response.error || 'Error al iniciar sesión' }
      }
    } catch (error) {
      return { success: false, error: 'Error de conexión' }
    }
  }

  const register = async (email: string, password: string) => {
    try {
      const response = await auth.register({ email, password })
      if (response.data) {
        return { success: true }
      } else {
        return { success: false, error: response.error || 'Error al registrarse' }
      }
    } catch (error) {
      return { success: false, error: 'Error de conexión' }
    }
  }

  const logout = () => {
    auth.logout()
    setUser(null)
    router.push('/')
  }

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
