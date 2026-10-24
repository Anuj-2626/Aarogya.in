import { AlertCircle } from 'lucide-react'

import { Button } from '@/components/ui/button'

interface ErrorStateProps {
  message?: string
  onRetry?: () => void
}

function ErrorState({
  message = 'Something went wrong. Please try again.',
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="flex min-h-48 items-center justify-center px-4">
      <div className="flex max-w-md flex-col items-center gap-4 text-center">
        <AlertCircle className="h-8 w-8 text-destructive" />

        <p className="text-sm text-muted-foreground">
          {message}
        </p>

        {onRetry && (
          <Button
            type="button"
            variant="outline"
            onClick={onRetry}
          >
            Try again
          </Button>
        )}
      </div>
    </div>
  )
}

export default ErrorState
