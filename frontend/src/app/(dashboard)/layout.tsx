'use client'

import { useVersionCheck } from '@/lib/hooks/use-version-check'
import { ErrorBoundary } from '@/components/common/ErrorBoundary'
import { ModalProvider } from '@/components/providers/ModalProvider'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Check for version updates once per session
  useVersionCheck()

  return (
    <ProtectedRoute>
      <ErrorBoundary>
        {children}
        <ModalProvider />
      </ErrorBoundary>
    </ProtectedRoute>
  )
}