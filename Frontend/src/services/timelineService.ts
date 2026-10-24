import api from './api'

import type { TimelineEvent } from '@/types/timeline'

export interface TimelineEventListResponse {
  patient_id: number
  events: TimelineEvent[]
  total_events: number
}

export const timelineService = {
  getSessionTimeline: async (
    sessionId: number,
  ): Promise<TimelineEvent[]> => {
    /*
     * The backend currently exposes the timeline
     * through the patient endpoint rather than a
     * session-specific endpoint.
     *
     * sessionId is retained in the method signature
     * so existing callers do not need to change.
     */
    void sessionId

    throw new Error(
      'Session-specific timeline endpoint is not available.',
    )
  },

  getPatientTimeline: async (
    patientId: number,
  ): Promise<TimelineEvent[]> => {
    const response =
      await api.get<TimelineEventListResponse>(
        `/timeline/patient/${patientId}`,
      )

    return response.data.events
  },

  getTimelineEvent: async (
    eventId: number,
  ): Promise<TimelineEvent> => {
    const response =
      await api.get<TimelineEvent>(
        `/timeline/events/${eventId}`,
      )

    return response.data
  },
}
