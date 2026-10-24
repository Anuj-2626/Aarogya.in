export interface TimelineEvent {
  event_id: number
  patient_id: number
  session_id?: number | null
  event_date?: string | null
  event_type: string
  title: string
  description?: string | null
  source_type: string
  source_id?: number | null
  structured_data?: string | null
  created_at: string
}