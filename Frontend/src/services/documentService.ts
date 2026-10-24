import api from './api'

import type {
  MedicalDocument,
  ProcessMedicalDocumentResponse,
} from '@/types/document'

export const documentService = {
  uploadDocument: async (
    sessionId: number,
    file: File,
  ): Promise<MedicalDocument> => {
    const formData = new FormData()

    formData.append('file', file)

    const response = await api.post<MedicalDocument>(
      '/documents/upload',
      formData,
      {
        params: {
          session_id: sessionId,
        },
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      },
    )

    return response.data
  },

  processDocument: async (
    documentId: number,
  ): Promise<ProcessMedicalDocumentResponse> => {
    const response =
      await api.post<ProcessMedicalDocumentResponse>(
        `/documents/${documentId}/process`,
      )

    return response.data
  },

  getSessionDocuments: async (
    sessionId: number,
  ): Promise<MedicalDocument[]> => {
    const response = await api.get<MedicalDocument[]>(
      `/documents/session/${sessionId}`,
    )

    return response.data
  },

  getDocument: async (
    documentId: number,
  ): Promise<MedicalDocument> => {
    const response = await api.get<MedicalDocument>(
      `/documents/${documentId}`,
    )

    return response.data
  },
}