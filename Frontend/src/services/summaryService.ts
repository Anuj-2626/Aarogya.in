import api from './api'

import type {
  ClinicalSummary,
  ClinicalSummaryListResponse,
} from '@/types/summary'

export const summaryService = {
  generateSummary: async (
    sessionId: number,
  ): Promise<ClinicalSummary> => {
    const response =
      await api.post<ClinicalSummary>(
        `/summaries/session/${sessionId}`,
      )

    return response.data
  },

  getSessionSummaries: async (
    sessionId: number,
  ): Promise<ClinicalSummaryListResponse> => {
    const response =
      await api.get<ClinicalSummaryListResponse>(
        `/summaries/session/${sessionId}`,
      )

    return response.data
  },

  getSummary: async (
    summaryId: number,
  ): Promise<ClinicalSummary> => {
    const response =
      await api.get<ClinicalSummary>(
        `/summaries/${summaryId}`,
      )

    return response.data
  },
}
