'use client'

import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuthStore } from '@/lib/stores/auth-store'
import { LoadingSpinner } from '@/components/common/LoadingSpinner'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter()
  const pathname = usePathname()
  const { isAuthenticated, hasHydrated, checkAuth, authRequired, checkAuthRequired } = useAuthStore()

  useEffect(() => {
    if (!hasHydrated) {
      return
    }

    const checkAuthentication = async () => {
      // First check if auth is required
      if (authRequired === null) {
        try {
          const required = await checkAuthRequired()
          if (!required) {
            // Auth not required, allow access
            return
          }
        } catch (error) {
          console.error('Error checking auth requirement:', error)
          // On error, assume auth is required
        }
      }

      // If auth is not required, allow access
      if (authRequired === false) {
        return
      }

      // Auth is required, check if user is authenticated
      if (!isAuthenticated) {
        // Store the current path for redirect after login
        sessionStorage.setItem('redirectAfterLogin', pathname)
        router.push('/login')
        return
      }

      // Verify the token is still valid
      const isValid = await checkAuth()
      if (!isValid) {
        sessionStorage.setItem('redirectAfterLogin', pathname)
        router.push('/login')
      }
    }

    checkAuthentication()
  }, [hasHydrated, isAuthenticated, authRequired, checkAuth, checkAuthRequired, router, pathname])

  // Show loading while hydrating or checking auth
  if (!hasHydrated || (authRequired === null)) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  // If auth is not required, show content
  if (authRequired === false) {
    return <>{children}</>
  }

  // If authenticated, show content
  if (isAuthenticated) {
    return <>{children}</>
  }

  // Otherwise, show loading while redirecting
  return (
    <div className="min-h-screen flex items-center justify-center">
      <LoadingSpinner />
    </div>
  )
}
