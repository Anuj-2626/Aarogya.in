import api from './api'

import type { Consent } from '@/types/consent'

export interface CreateConsentData {
  session_id: number
  consent_type: string
  status?: 'pending' | 'granted' | 'withdrawn'
}

export const consentService = {
  createConsent: async (
    data: CreateConsentData,
  ): Promise<Consent> => {
    const response = await api.post<Consent>(
      '/consents/',
      data,
    )

    return response.data
  },

  getConsent: async (
    consentId: number,
  ): Promise<Consent> => {
    const response = await api.get<Consent>(
      `/consents/${consentId}`,
    )

    return response.data
  },
}