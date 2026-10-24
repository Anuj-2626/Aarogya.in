import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { usePatient } from '@/contexts/PatientContext'
import { useTranslation } from '@/i18n/useTranslation'
import { sessionService } from '@/services/sessionService'

function PatientComplete() {
  const navigate = useNavigate()
  const {
    patient,
    session,
    clearPatientData,
  } = usePatient()
  const { t } = useTranslation()

  const completionStarted = useRef(false)

  const [isCompleting, setIsCompleting] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!session) {
      setIsCompleting(false)
      setError(t.complete.completionFailed)
      return
    }

    if (completionStarted.current) {
      return
    }

    completionStarted.current = true

    const completeSession = async () => {
      try {
        setIsCompleting(true)
        setError(null)

        if (session.status !== 'completed') {
          const updatedSession =
            await sessionService.updateSession(
              session.session_id,
              {
                status: 'completed',
              },
            )

          void updatedSession
        }
      } catch {
        setError(t.complete.completionFailed)
      } finally {
        setIsCompleting(false)
      }
    }

    void completeSession()
  }, [session, t.complete.completionFailed])

  const handleStartNew = () => {
    clearPatientData()
    navigate('/patient/register')
  }

  const handleReturnHome = () => {
    clearPatientData()
    navigate('/')
  }

  if (isCompleting) {
    return (
      <main className="flex min-h-96 items-center justify-center px-4">
        <div className="text-center">
          <h1 className="text-3xl font-bold">
            {t.complete.title}
          </h1>

          <p className="mt-2 text-muted-foreground">
            {t.complete.completing}
          </p>
        </div>
      </main>
    )
  }

  if (error) {
    return (
      <main className="flex min-h-96 items-center justify-center px-4">
        <div className="w-full max-w-xl rounded-xl border bg-card p-8 text-center shadow-sm">
          <h1 className="text-3xl font-bold">
            {t.common.error}
          </h1>

          <p className="mt-3 text-muted-foreground">
            {error}
          </p>

          <button
            type="button"
            onClick={() => window.location.reload()}
            className="mt-6 rounded-md bg-primary px-5 py-2.5 text-primary-foreground"
          >
            {t.common.retry}
          </button>
        </div>
      </main>
    )
  }

  return (
    <main className="flex min-h-96 items-center justify-center px-4 py-10">
      <div className="w-full max-w-2xl rounded-2xl border bg-card p-8 text-center shadow-sm">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
          <span className="text-3xl">✓</span>
        </div>

        <h1 className="mt-6 text-3xl font-bold">
          {t.complete.title}
        </h1>

        <p className="mx-auto mt-3 max-w-xl text-muted-foreground">
          {t.complete.description}
        </p>

        {(patient || session) && (
          <div className="mt-8 grid gap-4 rounded-xl border bg-muted/30 p-5 text-left sm:grid-cols-2">
            {patient && (
              <div>
                <p className="text-sm text-muted-foreground">
                  {t.complete.patient}
                </p>

                <p className="mt-1 font-medium">
                  {patient.name}
                </p>
              </div>
            )}

            {session && (
              <div>
                <p className="text-sm text-muted-foreground">
                  {t.complete.session}
                </p>

                <p className="mt-1 font-medium">
                  #{session.session_id}
                </p>
              </div>
            )}

            <div>
              <p className="text-sm text-muted-foreground">
                {t.complete.completed}
              </p>

              <p className="mt-1 font-medium">
                {t.complete.completed}
              </p>
            </div>
          </div>
        )}

        <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
          <button
            type="button"
            onClick={handleStartNew}
            className="rounded-md bg-primary px-5 py-2.5 text-primary-foreground"
          >
            {t.complete.startNew}
          </button>

          <button
            type="button"
            onClick={handleReturnHome}
            className="rounded-md border px-5 py-2.5"
          >
            {t.complete.returnHome}
          </button>
        </div>
      </div>
    </main>
  )
}

export default PatientComplete