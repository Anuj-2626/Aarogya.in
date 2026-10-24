import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  AlertCircle,
  ArrowRight,
  CalendarDays,
  FileText,
  HeartPulse,
  History,
  Loader2,
  MessageSquare,
  RefreshCw,
  Stethoscope,
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { usePatient } from '@/contexts/PatientContext'
import { useTranslation } from '@/i18n/useTranslation'
import { timelineService } from '@/services/timelineService'
import type { TimelineEvent } from '@/types/timeline'

function Timeline() {
  const navigate = useNavigate()
  const { session } = usePatient()
  const { t, language } = useTranslation()

  const [events, setEvents] = useState<TimelineEvent[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const locale =
    language === 'hi'
      ? 'hi-IN'
      : language === 'mr'
        ? 'mr-IN'
        : 'en-IN'

  const loadTimeline = useCallback(async () => {
    if (!session?.patient_id) {
      setError(t.timeline.sessionNotFound)
      setIsLoading(false)
      return
    }

    try {
      setIsLoading(true)
      setError(null)

      const response =
        await timelineService.getPatientTimeline(
          Number(session.patient_id),
        )

      const currentSessionId = session.session_id
        ? Number(session.session_id)
        : null

      const filteredEvents = response.filter(
        (event) =>
          event.session_id === null ||
          event.session_id === undefined ||
          Number(event.session_id) === currentSessionId,
      )

      setEvents(filteredEvents)
    } catch {
      setError(t.timeline.loadFailed)
    } finally {
      setIsLoading(false)
    }
  }, [
    session?.patient_id,
    session?.session_id,
    t.timeline,
  ])

  useEffect(() => {
    void loadTimeline()
  }, [loadTimeline])

  const sortedEvents = useMemo(() => {
    return [...events].sort((a, b) => {
      const dateA = a.event_date
        ? new Date(a.event_date).getTime()
        : new Date(a.created_at).getTime()

      const dateB = b.event_date
        ? new Date(b.event_date).getTime()
        : new Date(b.created_at).getTime()

      return dateB - dateA
    })
  }, [events])

  const getEventIcon = (eventType: string) => {
    const type = eventType.toLowerCase()

    if (
      type.includes('interview') ||
      type.includes('history')
    ) {
      return MessageSquare
    }

    if (
      type.includes('document') ||
      type.includes('ocr') ||
      type.includes('upload')
    ) {
      return FileText
    }

    if (
      type.includes('consult') ||
      type.includes('clinical')
    ) {
      return Stethoscope
    }

    if (
      type.includes('health') ||
      type.includes('medical')
    ) {
      return HeartPulse
    }

    return History
  }

  const getEventLabel = (eventType: string) => {
    const normalized = eventType.toLowerCase()

    if (normalized.includes('interview')) {
      return t.timeline.eventTypes.interview
    }

    if (normalized.includes('history')) {
      return t.timeline.eventTypes.history
    }

    if (normalized.includes('document')) {
      return t.timeline.eventTypes.document
    }

    if (normalized.includes('ocr')) {
      return t.timeline.eventTypes.ocr
    }

    if (normalized.includes('consultation')) {
      return t.timeline.eventTypes.consultation
    }

    if (normalized.includes('clinical')) {
      return t.timeline.eventTypes.clinical
    }

    if (normalized.includes('health')) {
      return t.timeline.eventTypes.health
    }

    if (normalized.includes('medical')) {
      return t.timeline.eventTypes.medical
    }

    if (normalized.includes('upload')) {
      return t.timeline.eventTypes.upload
    }

    return eventType
  }

  const formatDate = (
    eventDate: string | null | undefined,
    createdAt: string,
  ) => {
    const value = eventDate || createdAt
    const date = new Date(value)

    if (Number.isNaN(date.getTime())) {
      return t.timeline.dateUnavailable
    }

    return date.toLocaleString(locale, {
      dateStyle: 'medium',
      timeStyle: 'short',
    })
  }

  const handleContinue = () => {
    navigate('/patient/summary')
  }

  if (isLoading) {
    return (
      <main className="flex min-h-96 items-center justify-center px-6">
        <div className="flex flex-col items-center gap-3 text-center">
          <Loader2 className="h-8 w-8 animate-spin" />
          <p className="text-muted-foreground">
            {t.timeline.loading}
          </p>
        </div>
      </main>
    )
  }

  return (
    <main className="mx-auto w-full max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="space-y-6">
        {/* Header */}
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10">
              <CalendarDays className="h-6 w-6 text-primary" />
            </div>

            <div>
              <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
                {t.timeline.title}
              </h1>

              <p className="mt-1 text-sm text-muted-foreground sm:text-base">
                {t.timeline.description}
              </p>
            </div>
          </div>
        </div>

        {/* Error */}
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
                    onClick={() => void loadTimeline()}
                  >
                    <RefreshCw className="mr-2 h-4 w-4" />
                    {t.common.retry}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Timeline */}
        {sortedEvents.length > 0 ? (
          <section className="rounded-2xl border bg-card p-5 shadow-sm sm:p-6">
            <div className="space-y-6">
              {sortedEvents.map((event, index) => {
                const Icon = getEventIcon(event.event_type)

                return (
                  <div
                    key={event.event_id}
                    className="relative flex gap-4"
                  >
                    {index < sortedEvents.length - 1 && (
                      <div className="absolute left-[1.125rem] top-10 h-[calc(100%+1.5rem)] w-px bg-border" />
                    )}

                    <div className="relative z-10 flex h-9 w-9 shrink-0 items-center justify-center rounded-full border bg-background">
                      <Icon className="h-4 w-4 text-primary" />
                    </div>

                    <div className="min-w-0 flex-1 pb-2">
                      <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between sm:gap-4">
                        <div>
                          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                            {getEventLabel(event.event_type)}
                          </p>

                          <h2 className="mt-1 font-semibold">
                            {event.title}
                          </h2>
                        </div>

                        <time className="shrink-0 text-xs text-muted-foreground">
                          {formatDate(
                            event.event_date,
                            event.created_at,
                          )}
                        </time>
                      </div>

                      {event.description && (
                        <p className="mt-2 text-sm leading-6 text-muted-foreground">
                          {event.description}
                        </p>
                      )}

                      {event.source_type && (
                        <p className="mt-2 text-xs text-muted-foreground">
                          {event.source_type}
                        </p>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </section>
        ) : (
          !error && (
            <section className="rounded-2xl border bg-card p-6 text-center shadow-sm sm:p-10">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-muted">
                <History className="h-7 w-7 text-muted-foreground" />
              </div>

              <h2 className="mt-4 text-lg font-semibold">
                {t.timeline.noEventsTitle}
              </h2>

              <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-muted-foreground">
                {t.timeline.noEventsDescription}
              </p>
            </section>
          )
        )}

        {/* Continue to Clinical Summary */}
        <div className="flex justify-end border-t pt-5">
          <Button
            type="button"
            onClick={handleContinue}
          >
            {t.timeline.continue}
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </div>
    </main>
  )
}

export default Timeline
