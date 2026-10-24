import api from './api'

import type { Patient } from '@/types/patient'

export const patientService = {
  getPatient: async (
    patientId: string,
  ): Promise<Patient> => {
    const response = await api.get<Patient>(
      `/patients/${patientId}`,
    )

    return response.data
  },

  createPatient: async (
    data: Partial<Patient>,
  ): Promise<Patient> => {
    const response = await api.post<Patient>(
      '/patients/',
      data,
    )

    return response.data
  },
}