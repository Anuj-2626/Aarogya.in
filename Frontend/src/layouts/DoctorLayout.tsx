import { Outlet } from 'react-router-dom'

import AppLogo from '@/components/shared/AppLogo'

function DoctorLayout() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <AppLogo />

          <span className="text-sm text-muted-foreground">
            Doctor Portal
          </span>
        </div>
      </header>

      <main>
        <Outlet />
      </main>
    </div>
  )
}

export default DoctorLayout