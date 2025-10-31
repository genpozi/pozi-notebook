'use client'

import { useAuthStore } from '@/lib/stores/auth-store'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import type { LoginCredentials, SignupCredentials } from '@/lib/types/auth'

export function useAuth() {
  const router = useRouter()
  const {
    isAuthenticated,
    user,
    isLoading,
    login,
    signup,
    logout,
    checkAuth,
    checkAuthRequired,
    error,
    hasHydrated,
    authRequired
  } = useAuthStore()

  useEffect(() => {
    // Only check auth after the store has hydrated from localStorage
    if (hasHydrated) {
      // First check if auth is required
      if (authRequired === null) {
        checkAuthRequired().then((required) => {
          // If auth is required, check if we have valid credentials
          if (required) {
            checkAuth()
          }
        })
      } else if (authRequired) {
        // Auth is required, check credentials
        checkAuth()
      }
      // If authRequired === false, we're already authenticated (set in checkAuthRequired)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hasHydrated, authRequired])

  const handleLogin = async (credentials: LoginCredentials) => {
    const success = await login(credentials)
    if (success) {
      // Check if there's a stored redirect path
      const redirectPath = sessionStorage.getItem('redirectAfterLogin')
      if (redirectPath) {
        sessionStorage.removeItem('redirectAfterLogin')
        router.push(redirectPath)
      } else {
        router.push('/notebooks')
      }
    }
    return success
  }

  const handleSignup = async (credentials: SignupCredentials) => {
    const success = await signup(credentials)
    if (success) {
      router.push('/notebooks')
    }
    return success
  }

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  return {
    isAuthenticated,
    user,
    isLoading: isLoading || !hasHydrated, // Treat lack of hydration as loading
    error,
    login: handleLogin,
    signup: handleSignup,
    logout: handleLogout
  }
}