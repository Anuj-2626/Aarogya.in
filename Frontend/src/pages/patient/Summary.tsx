import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  FileText,
  Loader2,
  RefreshCw,
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { usePatient } from '@/contexts/PatientContext'
import { useTranslation } from '@/i18n/useTranslation'
import { summaryService } from '@/services/summaryService'
import type { ClinicalSummary } from '@/types/summary'

function Summary() {
  const navigate = useNavigate()
  const { session } = usePatient()
  const { t, language } = useTranslation()

  const [summary, setSummary] =
    useState<ClinicalSummary | null>(null)

  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const locale =
    language === 'hi'
      ? 'hi-IN'
      : language === 'mr'
        ? 'mr-IN'
        : 'en-IN'

  const loadSummary = useCallback(async () => {
    if (!session?.session_id) {
      setError(t.language.sessionNotFound)
      setIsLoading(false)
      return
    }

    try {
      setIsLoading(true)
      setError(null)

      const response =
        await summaryService.getSessionSummaries(
          Number(session.session_id),
        )

      if (response.summaries.length > 0) {
        const latestSummary =
          [...response.summaries].sort((a, b) => {
            const dateA = new Date(
              a.generated_at,
            ).getTime()

            const dateB = new Date(
              b.generated_at,
            ).getTime()

            return dateB - dateA
          })[0]

        setSummary(latestSummary)
      } else {
        setSummary(null)
      }
    } catch (requestError) {
      console.error(
        'Failed to load clinical summary:',
        requestError,
      )

      setSummary(null)

      setError(
        language === 'hi'
          ? 'मेडिकल सारांश लोड नहीं हो सका। कृपया पुनः प्रयास करें।'
          : language === 'mr'
            ? 'वैद्यकीय सारांश लोड करता आला नाही. कृपया पुन्हा प्रयत्न करा.'
            : 'Unable to load the medical summary. Please try again.',
      )
    } finally {
      setIsLoading(false)
    }
  }, [
    session?.session_id,
    language,
    t.language.sessionNotFound,
  ])

  useEffect(() => {
    void loadSummary()
  }, [loadSummary])

  const handleContinue = () => {
    navigate('/patient/complete')
  }

  if (isLoading) {
    return (
      <main className="flex min-h-96 items-center justify-center px-6">
        <div className="flex flex-col items-center gap-3 text-center">
          <Loader2 className="h-8 w-8 animate-spin" />

          <p className="text-muted-foreground">
            {t.common.loading}
          </p>
        </div>
      </main>
    )
  }

  return (
    <main className="mx-auto w-full max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="space-y-6">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10">
              <FileText className="h-6 w-6 text-primary" />
            </div>

            <div>
              <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
                {t.summary.title}
              </h1>

              <p className="mt-1 text-sm text-muted-foreground sm:text-base">
                {t.summary.description}
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="rounded-xl border border-destructive/30 bg-destructive/5 p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-destructive" />

              <div className="min-w-0 flex-1">
                <p className="font-medium text-destructive">
                  {t.common.error}
                </p>

                <p className="mt-1 text-sm text-muted-foreground">
                  {error}
                </p>

                <div className="mt-4">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => void loadSummary()}
                  >
                    <RefreshCw className="mr-2 h-4 w-4" />
                    {t.common.retry}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {summary && (
          <section className="rounded-2xl border bg-card p-5 shadow-sm sm:p-6">
            <div className="flex flex-col gap-3 border-b pb-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-5 w-5 text-green-600" />

                <div>
                  <h2 className="font-semibold">
                    {t.summary.title}
                  </h2>

                  <p className="text-xs text-muted-foreground">
                    {new Date(
                      summary.generated_at,
                    ).toLocaleString(locale)}
                  </p>
                </div>
              </div>

              <span className="w-fit rounded-full bg-muted px-3 py-1 text-xs font-medium capitalize">
                {summary.status}
              </span>
            </div>

            <div className="mt-5 whitespace-pre-wrap text-sm leading-7 text-foreground sm:text-base">
              {summary.summary_text}
            </div>
          </section>
        )}

        {!summary && !error && (
          <section className="rounded-2xl border bg-card p-6 text-center shadow-sm sm:p-10">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-muted">
              <FileText className="h-7 w-7 text-muted-foreground" />
            </div>

            <h2 className="mt-4 text-lg font-semibold">
              {t.summary.title}
            </h2>

            <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-muted-foreground">
              {t.summary.description}
            </p>
          </section>
        )}

        <div className="flex justify-end border-t pt-5">
          <Button
            type="button"
            onClick={handleContinue}
          >
            {t.summary.continue}

            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </div>
    </main>
  )
}

export default Summary
