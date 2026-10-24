import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  AlertCircle,
  ArrowLeft,
  CalendarDays,
  ClipboardList,
  FileText,
  HeartPulse,
  Languages,
  Loader2,
  MessageSquare,
  Stethoscope,
  UserRound,
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

import { patientService } from '@/services/patientService'
import { timelineService } from '@/services/timelineService'
import { summaryService } from '@/services/summaryService'
import { documentService } from '@/services/documentService'
import { interviewService } from '@/services/interviewService'

import type { Patient } from '@/types/patient'
import type { TimelineEvent } from '@/types/timeline'
import type { ClinicalSummary } from '@/types/summary'
import type { MedicalDocument } from '@/types/document'
import type {
  Answer,
  Interview,
  Question,
} from '@/types/interview'

function formatDate(value?: string | null) {
  if (!value) {
    return 'Not available'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return date.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

function formatDateTime(value?: string | null) {
  if (!value) {
    return 'Not available'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return date.toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function getLanguageName(language?: string | null) {
  switch (language) {
    case 'hi':
      return 'Hindi'
    case 'mr':
      return 'Marathi'
    case 'en':
      return 'English'
    default:
      return language ?? 'Not available'
  }
}

function getDocumentStatus(status?: string) {
  switch (status) {
    case 'completed':
      return 'OCR completed'
    case 'processing':
      return 'OCR processing'
    case 'pending':
      return 'OCR pending'
    case 'failed':
      return 'OCR failed'
    default:
      return status || 'Unknown'
  }
}

function getInterviewStatus(status?: Interview['status']) {
  switch (status) {
    case 'completed':
      return 'Completed'
    case 'in_progress':
      return 'In progress'
    case 'not_started':
      return 'Not started'
    default:
      return 'Unknown'
  }
}

function parseStructuredData(value?: string | null) {
  if (!value) {
    return null
  }

  try {
    return JSON.parse(value) as unknown
  } catch {
    return value
  }
}

function findAnswerText(
  questions: Question[],
  answers: Answer[],
  codes: string[],
) {
  const normalizedCodes = new Set(
    codes.map((code) => code.toLowerCase()),
  )

  for (const question of questions) {
    if (
      normalizedCodes.has(
        question.question_code.toLowerCase(),
      )
    ) {
      const answer = answers.find(
        (item) => item.question_id === question.question_id,
      )

      if (answer?.answer_text?.trim()) {
        return answer.answer_text.trim()
      }
    }
  }

  return null
}

function PatientView() {
  const { patientId } = useParams<{ patientId: string }>()
  const navigate = useNavigate()

  const [patient, setPatient] = useState<Patient | null>(null)
  const [timeline, setTimeline] = useState<TimelineEvent[]>([])
  const [documents, setDocuments] = useState<MedicalDocument[]>([])
  const [interviews, setInterviews] = useState<Interview[]>([])
  const [latestSummary, setLatestSummary] =
    useState<ClinicalSummary | null>(null)
  const [questions, setQuestions] = useState<Question[]>([])
  const [answers, setAnswers] = useState<Answer[]>([])

  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!patientId) {
      setError('Patient ID is missing.')
      setIsLoading(false)
      return
    }

    const numericPatientId = Number(patientId)

    if (Number.isNaN(numericPatientId)) {
      setError('Invalid patient ID.')
      setIsLoading(false)
      return
    }

    let cancelled = false

    const loadClinicalView = async () => {
      setIsLoading(true)
      setError(null)

      try {
        const [
          patientData,
          timelineData,
          allInterviews,
        ] = await Promise.all([
          patientService.getPatient(patientId),
          timelineService.getPatientTimeline(numericPatientId),
          interviewService.getInterviews(),
        ])

        if (cancelled) {
          return
        }

        setPatient(patientData)
        setTimeline(timelineData)

        /*
         * The backend exposes interviews globally.
         * Timeline events contain both patient_id and session_id,
         * allowing us to identify sessions belonging to this patient.
         */
        const patientSessionIds = new Set(
          timelineData
            .filter(
              (event) =>
                event.patient_id === numericPatientId &&
                typeof event.session_id === 'number',
            )
            .map((event) => event.session_id as number),
        )

        const patientInterviews = allInterviews
          .filter((interview) =>
            patientSessionIds.has(interview.session_id),
          )
          .sort(
            (a, b) =>
              new Date(b.created_at).getTime() -
              new Date(a.created_at).getTime(),
          )

        setInterviews(patientInterviews)

        /*
         * Documents are session based, so retrieve documents
         * belonging to the patient's known sessions.
         */
        if (patientSessionIds.size > 0) {
          const documentResults = await Promise.all(
            Array.from(patientSessionIds).map((sessionId) =>
              documentService.getSessionDocuments(sessionId),
            ),
          )

          if (cancelled) {
            return
          }

          const uniqueDocuments = new Map<
            number,
            MedicalDocument
          >()

          for (const documentList of documentResults) {
            for (const document of documentList) {
              uniqueDocuments.set(
                document.document_id,
                document,
              )
            }
          }

          setDocuments(
            Array.from(uniqueDocuments.values()).sort(
              (a, b) =>
                new Date(b.created_at).getTime() -
                new Date(a.created_at).getTime(),
            ),
          )
        } else {
          setDocuments([])
        }

        const latestInterview = patientInterviews[0]

        if (!latestInterview) {
          return
        }

        const [
          questionData,
          answerData,
          summaryResponse,
        ] = await Promise.all([
          interviewService.getQuestions(
            latestInterview.interview_id,
          ),
          interviewService.getAnswers(
            latestInterview.interview_id,
          ),
          summaryService.getSessionSummaries(
            latestInterview.session_id,
          ),
        ])

        if (cancelled) {
          return
        }

        setQuestions(questionData)
        setAnswers(answerData)

        const summaries = [...summaryResponse.summaries].sort(
          (a, b) =>
            new Date(b.generated_at).getTime() -
            new Date(a.generated_at).getTime(),
        )

        setLatestSummary(summaries[0] ?? null)
      } catch (requestError) {
        if (cancelled) {
          return
        }

        if (
          typeof requestError === 'object' &&
          requestError !== null &&
          'response' in requestError
        ) {
          const response = (
            requestError as {
              response?: {
                data?: {
                  detail?: string
                }
              }
            }
          ).response

          setError(
            response?.data?.detail ??
              'Unable to load the patient clinical information.',
          )
        } else if (requestError instanceof Error) {
          setError(requestError.message)
        } else {
          setError(
            'Unable to connect to Aarogya.in.',
          )
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false)
        }
      }
    }

    void loadClinicalView()

    return () => {
      cancelled = true
    }
  }, [patientId])

  const latestInterview = interviews[0] ?? null

  const ayushAnswer = useMemo(
    () =>
      findAnswerText(
        questions,
        answers,
        ['AYUSH_USE', 'AYUSH_DETAILS'],
      ),
    [questions, answers],
  )

  const clinicalProblem = useMemo(
    () =>
      findAnswerText(
        questions,
        answers,
        [
          'CHIEF_COMPLAINT',
          'MAIN_PROBLEM',
          'PRESENTING_COMPLAINT',
          'SYMPTOMS',
        ],
      ),
    [questions, answers],
  )

  const medications = useMemo(
    () =>
      findAnswerText(
        questions,
        answers,
        [
          'CURRENT_MEDICATIONS',
          'MEDICATIONS',
          'CURRENT_MEDICINES',
        ],
      ),
    [questions, answers],
  )

  const allergies = useMemo(
    () =>
      findAnswerText(
        questions,
        answers,
        [
          'ALLERGIES',
          'KNOWN_ALLERGIES',
        ],
      ),
    [questions, answers],
  )

  const redFlagAnswers = useMemo(() => {
    const redFlagCodes = [
      'CHEST_PAIN',
      'BREATHING_DIFFICULTY',
      'FAINTING',
      'LOSS_OF_CONSCIOUSNESS',
      'CONFUSION',
    ]

    return questions
      .filter((question) =>
        redFlagCodes.some((code) =>
          question.question_code
            .toLowerCase()
            .includes(code.toLowerCase()),
        ),
      )
      .map((question) => {
        const answer = answers.find(
          (item) =>
            item.question_id === question.question_id,
        )

        return {
          question: question.question_text,
          answer: answer?.answer_text ?? 'Not answered',
        }
      })
  }, [questions, answers])

  const sortedTimeline = useMemo(
    () =>
      [...timeline].sort((a, b) => {
        const dateA = new Date(
          a.event_date ?? a.created_at,
        ).getTime()

        const dateB = new Date(
          b.event_date ?? b.created_at,
        ).getTime()

        return dateB - dateA
      }),
    [timeline],
  )

  const handleConsultation = () => {
    if (!latestInterview) {
      return
    }

    navigate(
      `/doctor/consultation/${latestInterview.session_id}`,
    )
  }

  if (isLoading) {
    return (
      <main className="min-h-[calc(100vh-4rem)] bg-muted/20 px-4 py-6 md:px-6">
        <div className="mx-auto flex min-h-[60vh] max-w-7xl items-center justify-center">
          <div className="text-center">
            <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary" />
            <p className="mt-3 text-sm text-muted-foreground">
              Loading patient clinical information...
            </p>
          </div>
        </div>
      </main>
    )
  }

  if (error || !patient) {
    return (
      <main className="min-h-[calc(100vh-4rem)] bg-muted/20 px-4 py-6 md:px-6">
        <div className="mx-auto max-w-4xl">
          <Button
            variant="ghost"
            onClick={() => navigate('/doctor/dashboard')}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to dashboard
          </Button>

          <div className="mt-6 flex items-start gap-3 rounded-lg border border-destructive/30 bg-destructive/10 p-5">
            <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-destructive" />

            <div>
              <h1 className="font-semibold text-destructive">
                Unable to load patient
              </h1>

              <p className="mt-1 text-sm text-destructive/90">
                {error ?? 'Patient information was not found.'}
              </p>
            </div>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-[calc(100vh-4rem)] bg-muted/20 px-4 py-6 md:px-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <Button
            variant="ghost"
            onClick={() => navigate('/doctor/dashboard')}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to dashboard
          </Button>

          {latestInterview && (
            <Button onClick={handleConsultation}>
              <Stethoscope className="mr-2 h-4 w-4" />
              Open consultation
            </Button>
          )}
        </div>

        <section>
          <div className="flex items-start gap-4">
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-primary/10">
              <UserRound className="h-7 w-7 text-primary" />
            </div>

            <div>
              <p className="text-sm text-muted-foreground">
                Patient ID #{patient.patient_id}
              </p>

              <h1 className="text-3xl font-bold tracking-tight">
                {patient.name}
              </h1>

              <p className="mt-1 text-muted-foreground">
                Patient Clinical View
              </p>
            </div>
          </div>
        </section>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <InfoCard
            label="Date of birth"
            value={formatDate(patient.date_of_birth)}
            icon={<CalendarDays className="h-5 w-5" />}
          />

          <InfoCard
            label="Gender"
            value={patient.gender ?? 'Not available'}
            icon={<UserRound className="h-5 w-5" />}
          />

          <InfoCard
            label="Preferred language"
            value={getLanguageName(
              patient.preferred_language,
            )}
            icon={<Languages className="h-5 w-5" />}
          />

          <InfoCard
            label="Phone"
            value={patient.phone ?? 'Not available'}
            icon={<HeartPulse className="h-5 w-5" />}
          />
        </section>

        <section className="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(300px,1fr)]">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ClipboardList className="h-5 w-5" />
                Clinical Summary
              </CardTitle>

              <CardDescription>
                Latest generated clinical summary.
              </CardDescription>
            </CardHeader>

            <CardContent>
              {latestSummary ? (
                <div className="space-y-4">
                  <div className="rounded-lg border bg-muted/20 p-4">
                    <p className="whitespace-pre-wrap text-sm leading-6">
                      {latestSummary.summary_text}
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
                    <span>
                      Status: {latestSummary.status}
                    </span>

                    <span>
                      Generated:{' '}
                      {formatDateTime(
                        latestSummary.generated_at,
                      )}
                    </span>
                  </div>

                  {latestSummary.structured_data && (
                    <details className="rounded-lg border p-4">
                      <summary className="cursor-pointer text-sm font-medium">
                        Structured clinical data
                      </summary>

                      <pre className="mt-3 max-h-80 overflow-auto whitespace-pre-wrap break-words text-xs text-muted-foreground">
                        {JSON.stringify(
                          parseStructuredData(
                            latestSummary.structured_data,
                          ),
                          null,
                          2,
                        )}
                      </pre>
                    </details>
                  )}
                </div>
              ) : (
                <EmptyState
                  title="No clinical summary available"
                  description="A generated clinical summary will appear here when available."
                  icon={
                    <ClipboardList className="mx-auto h-8 w-8 text-muted-foreground" />
                  }
                />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Clinical Interview
              </CardTitle>

              <CardDescription>
                Latest patient history interview.
              </CardDescription>
            </CardHeader>

            <CardContent>
              {latestInterview ? (
                <div className="space-y-4 text-sm">
                  <DetailRow
                    label="Type"
                    value={latestInterview.interview_type.replace(
                      /_/g,
                      ' ',
                    )}
                  />

                  <DetailRow
                    label="Status"
                    value={getInterviewStatus(
                      latestInterview.status,
                    )}
                  />

                  <DetailRow
                    label="Language"
                    value={getLanguageName(
                      latestInterview.language,
                    )}
                  />

                  <DetailRow
                    label="Started"
                    value={formatDateTime(
                      latestInterview.started_at,
                    )}
                  />

                  <DetailRow
                    label="Completed"
                    value={formatDateTime(
                      latestInterview.completed_at,
                    )}
                  />

                  <div className="rounded-lg bg-muted/40 p-3">
                    <p className="text-xs text-muted-foreground">
                      Answers recorded
                    </p>

                    <p className="mt-1 text-xl font-bold">
                      {answers.length}
                    </p>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  No clinical interview is available for this patient.
                </p>
              )}
            </CardContent>
          </Card>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Key Clinical Information</CardTitle>

              <CardDescription>
                Important information captured during the interview.
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
              <ClinicalInfo
                label="Main problem"
                value={clinicalProblem}
              />

              <ClinicalInfo
                label="Current medications"
                value={medications}
              />

              <ClinicalInfo
                label="Known allergies"
                value={allergies}
              />

              <ClinicalInfo
                label="AYUSH / traditional treatment"
                value={ayushAnswer}
              />

              {!clinicalProblem &&
                !medications &&
                !allergies &&
                !ayushAnswer && (
                  <div className="rounded-lg border border-dashed p-5 text-center">
                    <p className="text-sm text-muted-foreground">
                      Key clinical information is not available in the current interview.
                    </p>
                  </div>
                )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5" />
                Safety / Red Flags
              </CardTitle>

              <CardDescription>
                Responses to safety-related clinical questions.
              </CardDescription>
            </CardHeader>

            <CardContent>
              {redFlagAnswers.length > 0 ? (
                <div className="space-y-3">
                  {redFlagAnswers.map((item, index) => (
                    <div
                      key={`${item.question}-${index}`}
                      className="rounded-lg border p-3"
                    >
                      <p className="text-sm font-medium">
                        {item.question}
                      </p>

                      <p className="mt-1 text-sm text-muted-foreground">
                        Answer: {item.answer}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState
                  title="No safety responses available"
                  description="No safety-related interview responses are available."
                  icon={
                    <AlertCircle className="mx-auto h-8 w-8 text-muted-foreground" />
                  }
                />
              )}
            </CardContent>
          </Card>
        </section>

        <section>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Medical Documents
              </CardTitle>

              <CardDescription>
                Documents uploaded during the patient workflow.
              </CardDescription>
            </CardHeader>

            <CardContent>
              {documents.length > 0 ? (
                <div className="divide-y rounded-lg border">
                  {documents.map((document) => (
                    <div
                      key={document.document_id}
                      className="flex flex-col gap-3 p-4 md:flex-row md:items-center md:justify-between"
                    >
                      <div className="flex items-start gap-3">
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-muted">
                          <FileText className="h-5 w-5" />
                        </div>

                        <div>
                          <p className="font-medium">
                            {document.filename}
                          </p>

                          <p className="mt-1 text-sm text-muted-foreground">
                            {document.file_type}
                            {' · '}
                            Uploaded{' '}
                            {formatDateTime(
                              document.created_at,
                            )}
                          </p>

                          {document.document_date && (
                            <p className="mt-1 text-xs text-muted-foreground">
                              Document date:{' '}
                              {formatDate(
                                document.document_date,
                              )}
                            </p>
                          )}
                        </div>
                      </div>

                      <div className="rounded-full border px-3 py-1 text-xs font-medium">
                        {getDocumentStatus(
                          document.ocr_status,
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState
                  title="No medical documents"
                  description="No medical documents are available for this patient's recorded sessions."
                  icon={
                    <FileText className="mx-auto h-8 w-8 text-muted-foreground" />
                  }
                />
              )}
            </CardContent>
          </Card>
        </section>

        <section>
          <Card>
            <CardHeader>
              <CardTitle>Medical Timeline</CardTitle>

              <CardDescription>
                Chronological history of recorded clinical events.
              </CardDescription>
            </CardHeader>

            <CardContent>
              {sortedTimeline.length > 0 ? (
                <div className="space-y-4">
                  {sortedTimeline.map((event) => (
                    <div
                      key={event.event_id}
                      className="flex gap-4"
                    >
                      <div className="flex flex-col items-center">
                        <div className="mt-1 h-3 w-3 shrink-0 rounded-full bg-primary" />

                        <div className="mt-2 h-full w-px bg-border" />
                      </div>

                      <div className="min-w-0 flex-1 pb-4">
                        <div className="flex flex-col gap-1 md:flex-row md:items-center md:justify-between">
                          <h3 className="font-semibold">
                            {event.title}
                          </h3>

                          <span className="text-xs text-muted-foreground">
                            {formatDate(
                              event.event_date ??
                                event.created_at,
                            )}
                          </span>
                        </div>

                        <p className="mt-1 text-xs uppercase tracking-wide text-muted-foreground">
                          {event.event_type}
                        </p>

                        {event.description && (
                          <p className="mt-2 text-sm leading-6 text-muted-foreground">
                            {event.description}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState
                  title="No timeline events"
                  description="No clinical events have been recorded for this patient yet."
                  icon={
                    <CalendarDays className="mx-auto h-8 w-8 text-muted-foreground" />
                  }
                />
              )}
            </CardContent>
          </Card>
        </section>

        {latestInterview && (
          <section className="flex justify-end pb-6">
            <Button
              size="lg"
              onClick={handleConsultation}
            >
              <Stethoscope className="mr-2 h-5 w-5" />
              Continue to consultation
            </Button>
          </section>
        )}
      </div>
    </main>
  )
}

interface InfoCardProps {
  label: string
  value: string
  icon: React.ReactNode
}

function InfoCard({
  label,
  value,
  icon,
}: InfoCardProps) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <CardDescription>{label}</CardDescription>

        <CardTitle className="flex items-center gap-2 text-lg">
          {icon}
          <span className="truncate">{value}</span>
        </CardTitle>
      </CardHeader>
    </Card>
  )
}

interface DetailRowProps {
  label: string
  value: string
}

function DetailRow({
  label,
  value,
}: DetailRowProps) {
  return (
    <div>
      <p className="text-muted-foreground">{label}</p>
      <p className="font-medium capitalize">{value}</p>
    </div>
  )
}

interface ClinicalInfoProps {
  label: string
  value: string | null
}

function ClinicalInfo({
  label,
  value,
}: ClinicalInfoProps) {
  return (
    <div className="rounded-lg border p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {label}
      </p>

      <p className="mt-2 text-sm leading-6">
        {value ?? 'Not recorded'}
      </p>
    </div>
  )
}

interface EmptyStateProps {
  title: string
  description: string
  icon: React.ReactNode
}

function EmptyState({
  title,
  description,
  icon,
}: EmptyStateProps) {
  return (
    <div className="rounded-lg border border-dashed p-6 text-center">
      {icon}

      <p className="mt-3 font-medium">
        {title}
      </p>

      <p className="mt-1 text-sm text-muted-foreground">
        {description}
      </p>
    </div>
  )
}

export default PatientView