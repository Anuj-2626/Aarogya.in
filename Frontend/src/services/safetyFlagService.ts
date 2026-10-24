import api from './api'

import type { SafetyFlag } from '@/types/safetyFlag'

export const safetyFlagService = {
  getInterviewSafetyFlags: async (
    interviewId: number,
  ): Promise<SafetyFlag[]> => {
    const response = await api.get<SafetyFlag[]>(
      `/safety-flags/interview/${interviewId}`,
    )

    return response.data
  },
}