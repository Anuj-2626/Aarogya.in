import { HeartPulse } from 'lucide-react'

interface AppLogoProps {
  showIcon?: boolean
}

function AppLogo({
  showIcon = true,
}: AppLogoProps) {
  return (
    <div className="flex items-center gap-2">
      {showIcon && (
        <HeartPulse className="h-5 w-5" />
      )}

      <span className="text-lg font-semibold">
        Aarogya.in
      </span>
    </div>
  )
}

export default AppLogo