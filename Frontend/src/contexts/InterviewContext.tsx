import {
  createContext,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

import type {
  Answer,
  Interview,
  Question,
} from '@/types/interview'
import type { SafetyFlag } from '@/types/safetyFlag'

interface InterviewContextValue {
  interview: Interview | null
  questions: Question[]
  answers: Answer[]
  safetyFlags: SafetyFlag[]

  currentQuestion: Question | null

  isLoading: boolean
  isSubmitting: boolean
  error: string | null

  setInterview: (interview: Interview | null) => void
  setQuestions: (questions: Question[]) => void
  setAnswers: (answers: Answer[]) => void
  setSafetyFlags: (safetyFlags: SafetyFlag[]) => void

  clearInterviewData: () => void
}

interface InterviewProviderProps {
  children: ReactNode
}

const InterviewContext = createContext<
  InterviewContextValue | undefined
>(undefined)

export function InterviewProvider({
  children,
}: InterviewProviderProps) {
  const [interview, setInterview] =
    useState<Interview | null>(null)

  const [questions, setQuestions] = useState<Question[]>([])

  const [answers, setAnswers] = useState<Answer[]>([])

  const [safetyFlags, setSafetyFlags] = useState<SafetyFlag[]>(
    [],
  )

  const [isLoading, setIsLoading] = useState(false)

  const [isSubmitting, setIsSubmitting] = useState(false)

  const [error, setError] = useState<string | null>(null)

  const currentQuestion = useMemo(() => {
    if (!interview?.current_question_id) {
      return null
    }

    return (
      questions.find(
        (question) =>
          question.question_id ===
          interview.current_question_id,
      ) ?? null
    )
  }, [interview, questions])

  const clearInterviewData = () => {
    setInterview(null)
    setQuestions([])
    setAnswers([])
    setSafetyFlags([])
    setIsLoading(false)
    setIsSubmitting(false)
    setError(null)
  }

  const value = useMemo(
    () => ({
      interview,
      questions,
      answers,
      safetyFlags,
      currentQuestion,
      isLoading,
      isSubmitting,
      error,
      setInterview,
      setQuestions,
      setAnswers,
      setSafetyFlags,
      clearInterviewData,
    }),
    [
      interview,
      questions,
      answers,
      safetyFlags,
      currentQuestion,
      isLoading,
      isSubmitting,
      error,
    ],
  )

  return (
    <InterviewContext.Provider value={value}>
      {children}
    </InterviewContext.Provider>
  )
}

export function useInterview() {
  const context = useContext(InterviewContext)

  if (!context) {
    throw new Error(
      'useInterview must be used within an InterviewProvider',
    )
  }

  return context
}