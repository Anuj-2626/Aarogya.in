import api from './api'

import type {
  Answer,
  Interview,
  Question,
} from '@/types/interview'

export type SupportedLanguage = 'en' | 'hi' | 'mr'

export interface CreateInterviewData {
  session_id: number
  interview_type?: string
  language?: SupportedLanguage
}

export interface UpdateInterviewData {
  status?: 'not_started' | 'in_progress' | 'completed'
  language?: SupportedLanguage
}

export interface CreateAnswerData {
  interview_id: number
  question_id: number
  answer_text: string
  answer_type?: string
}

export const interviewService = {
  createInterview: async (
    data: CreateInterviewData,
  ): Promise<Interview> => {
    const response = await api.post<Interview>(
      '/interviews/',
      data,
    )

    return response.data
  },

  getInterviews: async (): Promise<Interview[]> => {
    const response = await api.get<Interview[]>(
      '/interviews/',
    )

    return response.data
  },

  getInterview: async (
    interviewId: number,
  ): Promise<Interview> => {
    const response = await api.get<Interview>(
      `/interviews/${interviewId}`,
    )

    return response.data
  },

  updateInterview: async (
    interviewId: number,
    data: UpdateInterviewData,
  ): Promise<Interview> => {
    const response = await api.put<Interview>(
      `/interviews/${interviewId}`,
      data,
    )

    return response.data
  },

  getQuestions: async (
    interviewId: number,
  ): Promise<Question[]> => {
    const response = await api.get<Question[]>(
      `/questions/interview/${interviewId}`,
    )

    return response.data
  },

  submitAnswer: async (
    data: CreateAnswerData,
  ): Promise<Answer> => {
    const response = await api.post<Answer>(
      '/answers/',
      data,
    )

    return response.data
  },

  getAnswers: async (
    interviewId: number,
  ): Promise<Answer[]> => {
    const response = await api.get<Answer[]>(
      `/answers/interview/${interviewId}`,
    )

    return response.data
  },
}