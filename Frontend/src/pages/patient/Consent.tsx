import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckCircle2, ShieldCheck } from 'lucide-react'

import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

import { usePatient } from '@/contexts/PatientContext'
import { consentService } from '@/services/consentService'

function Consent() {
  const navigate = useNavigate()
  const { session, setConsent } = usePatient()

  const [agreed, setAgreed] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [serverError, setServerError] = useState<string | null>(
    null,
  )

  const handleConsent = async () => {
    if (!session) {
      setServerError(
        'Your clinical intake session could not be found. Please restart the patient registration process.',
      )
      return
    }

    if (!agreed) {
      setServerError(
        'Please confirm that you understand and agree before continuing.',
      )
      return
    }

    setServerError(null)
    setIsSubmitting(true)

    try {
      const clinicalConsent =
        await consentService.createConsent({
          session_id: session.session_id,
          consent_type: 'clinical_workflow',
          status: 'granted',
        })

      await consentService.createConsent({
        session_id: session.session_id,
        consent_type: 'ai_processing',
        status: 'granted',
      })

      setConsent(clinicalConsent)

      navigate('/patient/language')
    } catch (error) {
      if (
        typeof error === 'object' &&
        error !== null &&
        'response' in error
      ) {
        const response = (
          error as {
            response?: {
              data?: {
                detail?: string
              }
            }
          }
        ).response

        setServerError(
          response?.data?.detail ??
            'Unable to record your consent. Please try again.',
        )
      } else {
        setServerError(
          'Unable to connect to Aarogya.in. Please try again.',
        )
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="min-h-[calc(100vh-4rem)] px-4 py-8">
      <div className="mx-auto flex w-full max-w-2xl items-center justify-center">
        <Card className="w-full">
          <CardHeader>
            <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
              <ShieldCheck className="h-6 w-6 text-primary" />
            </div>

            <CardTitle className="text-2xl">
              Your Consent
            </CardTitle>

            <CardDescription>
              Before we begin the clinical intake process,
              please review and confirm your consent.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-6">
            <div className="space-y-4 text-sm text-muted-foreground">
              <p>
                Aarogya.in will collect information about your
                health history to help healthcare professionals
                understand your condition and prepare for your
                consultation.
              </p>

              <p>
                The information you provide may include your
                symptoms, medical history, medications, allergies,
                previous medical records, and other relevant
                clinical information.
              </p>

              <p>
                Some information may be processed using
                AI-assisted technology to help organize your
                clinical history for healthcare professionals.
              </p>

              <p>
                Your information is intended to support your
                clinical care. Please provide accurate information
                to the best of your knowledge.
              </p>
            </div>

            <button
              type="button"
              onClick={() => {
                setAgreed((current) => !current)
                setServerError(null)
              }}
              className="flex w-full items-start gap-3 rounded-lg border p-4 text-left transition-colors hover:bg-muted/50"
            >
              <span
                className={[
                  'mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded border',
                  agreed
                    ? 'border-primary bg-primary text-primary-foreground'
                    : 'border-input',
                ].join(' ')}
              >
                {agreed && (
                  <CheckCircle2 className="h-4 w-4" />
                )}
              </span>

              <span className="text-sm leading-5">
                I understand the purpose of this clinical intake
                process and consent to providing my health
                information, including its processing by
                AI-assisted technology, for clinical care.
              </span>
            </button>

            {serverError && (
              <div className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2">
                <p className="text-sm text-destructive">
                  {serverError}
                </p>
              </div>
            )}

            <Button
              type="button"
              className="w-full"
              disabled={!agreed || isSubmitting}
              onClick={handleConsent}
            >
              {isSubmitting
                ? 'Recording Consent...'
                : 'I Agree & Continue'}
            </Button>
          </CardContent>
        </Card>
      </div>
    </main>
  )
}

export default Consent