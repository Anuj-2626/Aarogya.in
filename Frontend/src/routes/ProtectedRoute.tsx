import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { useAuth } from '@/contexts/AuthContext'

function ProtectedRoute() {
  const {
    user,
    isAuthenticated,
    isLoading,
  } = useAuth()

  const location = useLocation()

  if (isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center px-4">
        <div className="text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />

          <p className="mt-4 text-sm text-muted-foreground">
            Checking your session...
          </p>
        </div>
      </main>
    )
  }

  if (!isAuthenticated || !user) {
    return (
      <Navigate
        to="/doctor/login"
        replace
        state={{ from: location }}
      />
    )
  }

  if (
    user.role !== 'doctor' &&
    user.role !== 'admin'
  ) {
    return (
      <Navigate
        to="/doctor/login"
        replace
      />
    )
  }

  return <Outlet />
}

export default ProtectedRoute