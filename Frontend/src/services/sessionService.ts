import api from './api'

import type { Session } from '@/types/session'
import type { SupportedLanguage } from '@/i18n/translations'

export interface CreateSessionData {
  patient_id: number
  session_type?: string
  language?: SupportedLanguage
}

export interface UpdateSessionData {
  session_type?: string
  status?: string
  language?: SupportedLanguage
  consent_status?: string
}

export const sessionService = {
  getSession: async (
    sessionId: number,
  ): Promise<Session> => {
    const response = await api.get<Session>(
      `/sessions/${sessionId}`,
    )

    return response.data
  },

  createSession: async (
    data: CreateSessionData,
  ): Promise<Session> => {
    const response = await api.post<Session>(
      '/sessions/',
      data,
    )

    return response.data
  },

  updateSession: async (
    sessionId: number,
    data: UpdateSessionData,
  ): Promise<Session> => {
    const response = await api.put<Session>(
      `/sessions/${sessionId}`,
      data,
    )

    return response.data
  },
}
