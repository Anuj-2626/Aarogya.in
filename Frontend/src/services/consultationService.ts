import api from './api'

import type {
  Consultation,
  ConsultationListResponse,
  CreateConsultationData,
  UpdateConsultationData,
} from '@/types/consultation'


export const consultationService = {
  createConsultation: async (
    data: CreateConsultationData,
  ): Promise<Consultation> => {
    const response =
      await api.post<Consultation>(
        '/consultations/',
        data,
      )

    return response.data
  },

  getSessionConsultations: async (
    sessionId: number,
  ): Promise<ConsultationListResponse> => {
    const response =
      await api.get<ConsultationListResponse>(
        `/consultations/session/${sessionId}`,
      )

    return response.data
  },

  getConsultation: async (
    consultationId: number,
  ): Promise<Consultation> => {
    const response =
      await api.get<Consultation>(
        `/consultations/${consultationId}`,
      )

    return response.data
  },

  updateConsultation: async (
    consultationId: number,
    data: UpdateConsultationData,
  ): Promise<Consultation> => {
    const response =
      await api.put<Consultation>(
        `/consultations/${consultationId}`,
        data,
      )

    return response.data
  },

  completeConsultation: async (
    consultationId: number,
    data: Omit<
      UpdateConsultationData,
      'status'
    >,
  ): Promise<Consultation> => {
    const response =
      await api.put<Consultation>(
        `/consultations/${consultationId}`,
        {
          ...data,
          status: 'completed',
        },
      )

    return response.data
  },
}