import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react'
import {
  AlertTriangle,
  Bot,
  CheckCircle2,
  Send,
  UserRound,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'

import { usePatient } from '@/contexts/PatientContext'
import { useInterview } from '@/contexts/InterviewContext'
import { interviewService } from '@/services/interviewService'
import { safetyFlagService } from '@/services/safetyFlagService'
import { useTranslation } from '@/i18n/useTranslation'

function Interview() {
  const navigate = useNavigate()

  const { session } = usePatient()
  const { t } = useTranslation()

  const {
    interview,
    questions,
    answers,
    currentQuestion,
    safetyFlags,
    error,
    setInterview,
    setQuestions,
    setAnswers,
    setSafetyFlags,
  } = useInterview()

  const [answer, setAnswer] = useState('')
  const [isInitializing, setIsInitializing] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [pageError, setPageError] = useState<string | null>(null)

  /*
   * Prevent duplicate initialization requests.
   *
   * React development mode can run effects more than once.
   * Without this guard, two initialization requests can both
   * see interview === null and attempt to create an interview.
   */
  const initializationStarted = useRef(false)

  const activeSafetyFlags = useMemo(
    () =>
      safetyFlags.filter(
        (flag) => flag.status === 'active',
      ),
    [safetyFlags],
  )

  useEffect(() => {
    if (initializationStarted.current) {
      return
    }

    initializationStarted.current = true

    const initializeInterview = async () => {
      if (!session) {
        setPageError(
          'Your clinical intake session could not be found. Please restart the patient registration process.',
        )
        setIsInitializing(false)
        return
      }

      try {
        setPageError(null)

        let activeInterview = interview

        /*
         * If an interview already exists in context,
         * use it directly.
         */
        if (!activeInterview) {
          const existingInterviews =
            await interviewService.getInterviews()

          const currentSessionId = Number(
            session.session_id,
          )

          /*
           * Find an existing clinical-history interview
           * for this exact session.
           */
          activeInterview =
            existingInterviews.find(
              (item) =>
                Number(item.session_id) ===
                  currentSessionId &&
                item.interview_type ===
                  'clinical_history',
            ) ?? null

          /*
           * Create only when no interview exists.
           *
           * If another initialization request has already
           * created the interview, the backend may return 409.
           * In that case, fetch the existing interview and
           * continue instead of failing the patient flow.
           */
          if (!activeInterview) {
            try {
              activeInterview =
                await interviewService.createInterview({
                  session_id: currentSessionId,
                  interview_type: 'clinical_history',
                  language: session.language ?? 'en',
                })
            } catch (createError) {
              const status =
                typeof createError === 'object' &&
                createError !== null &&
                'response' in createError
                  ? (
                      createError as {
                        response?: {
                          status?: number
                        }
                      }
                    ).response?.status
                  : undefined

              /*
               * 409 means the backend confirms that an
               * interview already exists.
               *
               * Recover by fetching the interviews again.
               */
              if (status === 409) {
                const refreshedInterviews =
                  await interviewService.getInterviews()

                activeInterview =
                  refreshedInterviews.find(
                    (item) =>
                      Number(item.session_id) ===
                        currentSessionId &&
                      item.interview_type ===
                        'clinical_history',
                  ) ?? null

                if (!activeInterview) {
                  throw createError
                }
              } else {
                throw createError
              }
            }
          }
        }

        /*
         * Safety check in case initialization somehow reached
         * this point without an interview.
         */
        if (!activeInterview) {
          throw new Error(
            'Clinical interview could not be initialized.',
          )
        }

        /*
         * Always synchronize the interview language with the
         * language selected for the current patient session.
         *
         * This must happen whether the interview was:
         * - already present in context,
         * - found in the backend,
         * - or newly created.
         */
        const selectedLanguage =
          session.language ?? 'en'

        if (
          activeInterview.language !== selectedLanguage
        ) {
          activeInterview =
            await interviewService.updateInterview(
              activeInterview.interview_id,
              {
                language: selectedLanguage,
              },
            )
        }

        /*
         * Keep the synchronized interview in context.
         */
        setInterview(activeInterview)

        /*
         * Load all questions for the interview.
         *
         * The backend translates these questions according
         * to the interview language.
         */
        const interviewQuestions =
          await interviewService.getQuestions(
            activeInterview.interview_id,
          )

        setQuestions(interviewQuestions)

        /*
         * Load previously submitted answers.
         */
        const existingAnswers =
          await interviewService.getAnswers(
            activeInterview.interview_id,
          )

        setAnswers(existingAnswers)

        /*
         * Safety flags are supplementary.
         *
         * If this endpoint is unavailable, the interview
         * should continue working normally.
         */
        try {
          const existingFlags =
            await safetyFlagService.getInterviewSafetyFlags(
              activeInterview.interview_id,
            )

          setSafetyFlags(existingFlags)
        } catch {
          setSafetyFlags([])
        }
      } catch (requestError) {
        console.error(
          'Failed to initialize clinical interview:',
          requestError,
        )

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

          setPageError(
            response?.data?.detail ??
              'Unable to start the clinical interview. Please try again.',
          )
        } else if (
          requestError instanceof Error
        ) {
          setPageError(requestError.message)
        } else {
          setPageError(
            'Unable to connect to Aarogya.in. Please try again.',
          )
        }
      } finally {
        setIsInitializing(false)
      }
    }

    void initializeInterview()
  }, [
    session,
    interview,
    setInterview,
    setQuestions,
    setAnswers,
    setSafetyFlags,
  ])

  const currentQuestionIndex = useMemo(() => {
    if (!currentQuestion) {
      return -1
    }

    return questions.findIndex(
      (question) =>
        question.question_id ===
        currentQuestion.question_id,
    )
  }, [currentQuestion, questions])

  const progress = useMemo(() => {
    if (
      currentQuestionIndex === -1 ||
      questions.length === 0
    ) {
      return interview?.status === 'completed' ? 100 : 0
    }

    return Math.round(
      ((currentQuestionIndex + 1) / questions.length) *
        100,
    )
  }, [
    currentQuestionIndex,
    questions.length,
    interview?.status,
  ])

  const getQuestionText = (questionId: number) => {
    return (
      questions.find(
        (question) =>
          question.question_id === questionId,
      )?.question_text ?? 'Question'
    )
  }

  const handleSubmitAnswer = async () => {
    if (
      !interview ||
      !currentQuestion ||
      !answer.trim() ||
      isSubmitting
    ) {
      return
    }

    setPageError(null)
    setIsSubmitting(true)

    try {
      let activeInterview = interview

      /*
       * Start the interview when the first answer is submitted.
       */
      if (activeInterview.status === 'not_started') {
        activeInterview =
          await interviewService.updateInterview(
            activeInterview.interview_id,
            {
              status: 'in_progress',
            },
          )

        setInterview(activeInterview)
      }

      /*
       * Submit the answer.
       */
      const submittedAnswer =
        await interviewService.submitAnswer({
          interview_id: activeInterview.interview_id,
          question_id: currentQuestion.question_id,
          answer_text: answer.trim(),
          answer_type: 'text',
        })

      setAnswers([...answers, submittedAnswer])

      /*
       * Refresh interview state because the backend answer
       * endpoint updates current_question_id and may complete
       * the interview.
       */
      const updatedInterview =
        await interviewService.getInterview(
          activeInterview.interview_id,
        )

      setInterview(updatedInterview)

      /*
       * Refresh safety flags.
       */
      try {
        const updatedFlags =
          await safetyFlagService.getInterviewSafetyFlags(
            activeInterview.interview_id,
          )

        setSafetyFlags(updatedFlags)
      } catch {
        // Safety flag retrieval failure should not block
        // interview progression.
      }

      setAnswer('')

      /*
       * Continue to the document stage after completion.
       */
      if (updatedInterview.status === 'completed') {
        navigate('/patient/documents')
      }
    } catch (requestError) {
      console.error(
        'Failed to submit interview answer:',
        requestError,
      )

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

        setPageError(
          response?.data?.detail ??
            'Unable to submit your answer. Please try again.',
        )
      } else {
        setPageError(
          'Unable to connect to Aarogya.in. Please try again.',
        )
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  if (pageError || error) {
    return (
      <main className="min-h-[calc(100vh-4rem)] px-4 py-8">
        <div className="mx-auto flex w-full max-w-2xl items-center justify-center">
          <Card className="w-full">
            <CardHeader>
              <CardTitle>
                {t.interview.title}
              </CardTitle>
            </CardHeader>

            <CardContent>
              <div className="rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3">
                <p className="text-sm text-destructive">
                  {pageError ?? error}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    )
  }

  if (isInitializing) {
    return (
      <main className="min-h-[calc(100vh-4rem)] px-4 py-8">
        <div className="mx-auto flex min-h-[60vh] w-full max-w-2xl items-center justify-center">
          <div className="text-center">
            <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />

            <p className="text-sm text-muted-foreground">
              {t.common.loading}
            </p>
          </div>
        </div>
      </main>
    )
  }

  if (interview?.status === 'completed') {
    return (
      <main className="min-h-[calc(100vh-4rem)] px-4 py-8">
        <div className="mx-auto flex min-h-[60vh] w-full max-w-2xl items-center justify-center">
          <Card className="w-full">
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-primary/10">
                <CheckCircle2 className="h-7 w-7 text-primary" />
              </div>

              <CardTitle className="text-2xl">
                {t.interview.complete}
              </CardTitle>

              <CardDescription>
                {t.interview.description}
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-6">
              <div className="rounded-lg border bg-muted/40 p-4">
                <p className="text-sm leading-6 text-muted-foreground">
                  {t.interview.description}
                </p>
              </div>

              <Button
                type="button"
                className="w-full"
                onClick={() =>
                  navigate('/patient/documents')
                }
              >
                {t.documents.continue}
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>
    )
  }

  if (!interview || !currentQuestion) {
    return (
      <main className="min-h-[calc(100vh-4rem)] px-4 py-8">
        <div className="mx-auto flex min-h-[60vh] w-full max-w-2xl items-center justify-center">
          <Card className="w-full">
            <CardContent className="py-10 text-center">
              <h2 className="text-xl font-semibold">
                {t.interview.title}
              </h2>

              <p className="mt-2 text-sm text-muted-foreground">
                {t.interview.description}
              </p>
            </CardContent>
          </Card>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-[calc(100vh-4rem)] px-4 py-6">
      <div className="mx-auto w-full max-w-3xl">
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">
                {t.interview.title}
              </h1>

              <p className="mt-1 text-sm text-muted-foreground">
                {t.interview.description}
              </p>
            </div>

            <span className="text-sm text-muted-foreground">
              {currentQuestionIndex + 1} / {questions.length}
            </span>
          </div>

          <div className="mt-4 h-2 overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary transition-all"
              style={{
                width: `${progress}%`,
              }}
            />
          </div>
        </div>

        {activeSafetyFlags.length > 0 && (
          <Card className="mb-6 border-amber-500/40 bg-amber-50/50 dark:bg-amber-950/20">
            <CardContent className="flex gap-3 p-4">
              <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />

              <div>
                <p className="font-medium">
                  {t.interview.safetyTitle}
                </p>

                <p className="mt-1 text-sm leading-6 text-muted-foreground">
                  {t.interview.safetyDescription}
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="space-y-5">
          {answers.map((item) => (
            <div
              key={item.answer_id}
              className="space-y-3"
            >
              <div className="flex items-start gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10">
                  <Bot className="h-5 w-5 text-primary" />
                </div>

                <div className="max-w-[85%] rounded-2xl rounded-tl-sm bg-muted px-4 py-3">
                  <p className="text-sm leading-6">
                    {getQuestionText(item.question_id)}
                  </p>
                </div>
              </div>

              <div className="flex items-start justify-end gap-3">
                <div className="max-w-[85%] rounded-2xl rounded-tr-sm border bg-background px-4 py-3">
                  <p className="text-sm leading-6">
                    {item.answer_text}
                  </p>
                </div>

                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-muted">
                  <UserRound className="h-5 w-5 text-muted-foreground" />
                </div>
              </div>
            </div>
          ))}

          <div className="flex items-start gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10">
              <Bot className="h-5 w-5 text-primary" />
            </div>

            <div className="max-w-[85%] rounded-2xl rounded-tl-sm bg-muted px-4 py-3">
              <p className="text-sm leading-6">
                {currentQuestion.question_text}
              </p>
            </div>
          </div>

          <div className="flex items-start justify-end gap-3">
            <div className="max-w-[85%] rounded-2xl rounded-tr-sm border bg-background px-4 py-3">
              <Textarea
                value={answer}
                onChange={(event) =>
                  setAnswer(event.target.value)
                }
                onKeyDown={(event) => {
                  if (
                    event.key === 'Enter' &&
                    !event.shiftKey
                  ) {
                    event.preventDefault()

                    if (
                      answer.trim() &&
                      !isSubmitting
                    ) {
                      void handleSubmitAnswer()
                    }
                  }
                }}
                placeholder={t.interview.answerPlaceholder}
                disabled={isSubmitting}
                className="min-h-28 resize-none border-0 p-0 shadow-none focus-visible:ring-0"
              />
            </div>

            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-muted">
              <UserRound className="h-5 w-5 text-muted-foreground" />
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <Button
              type="button"
              disabled={!answer.trim() || isSubmitting}
              onClick={() => void handleSubmitAnswer()}
            >
              {isSubmitting
                ? t.common.loading
                : t.interview.next}

              <Send className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </main>
  )
}

export default Interview