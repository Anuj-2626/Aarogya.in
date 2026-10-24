import { Loader2 } from 'lucide-react'

interface LoadingStateProps {
  message?: string
}

function LoadingState({
  message = 'Loading...',
}: LoadingStateProps) {
  return (
    <div className="flex min-h-48 items-center justify-center">
      <div className="flex flex-col items-center gap-3 text-muted-foreground">
        <Loader2 className="h-6 w-6 animate-spin" />
        <p className="text-sm">{message}</p>
      </div>
    </div>
  )
}

export default LoadingState