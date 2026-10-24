import type { ReactNode } from 'react'

interface PageContainerProps {
  children: ReactNode
  className?: string
}

function PageContainer({
  children,
  className = '',
}: PageContainerProps) {
  return (
    <div
      className={`mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8 ${className}`}
    >
      {children}
    </div>
  )
}

export default PageContainer