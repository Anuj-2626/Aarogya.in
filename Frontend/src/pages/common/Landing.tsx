import { useNavigate } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import PageContainer from '@/components/shared/PageContainer'

function Landing() {
  const navigate = useNavigate()

  return (
    <main className="min-h-screen">
      <PageContainer>
        <div className="flex min-h-[calc(100vh-3rem)] flex-col items-center justify-center text-center">
          <h1 className="text-4xl font-bold tracking-tight">
            Aarogya.in
          </h1>

          <p className="mt-3 max-w-xl text-muted-foreground">
            AI-powered clinical intake platform for
            streamlined patient care.
          </p>

          <div className="mt-6 flex gap-3">
            <Button
              onClick={() => navigate('/patient/register')}
            >
              Patient Portal
            </Button>

            <Button
              variant="outline"
              onClick={() => navigate('/doctor/login')}
            >
              Doctor Portal
            </Button>
          </div>
        </div>
      </PageContainer>
    </main>
  )
}

export default Landing