export type ConsultationStatus =
  | 'draft'
  | 'completed'

export interface Consultation {
  consultation_id: number
  session_id: number
  doctor_user_id: number
  status: ConsultationStatus

  clinical_notes: string | null
  assessment: string | null
  diagnosis: string | null
  treatment_plan: string | null
  follow_up: string | null

  created_at: string
  updated_at: string
  completed_at: string | null
}

export interface ConsultationListResponse {
  session_id: number
  consultations: Consultation[]
  total_consultations: number
}

export interface CreateConsultationData {
  session_id: number
  clinical_notes?: string | null
  assessment?: string | null
  diagnosis?: string | null
  treatment_plan?: string | null
  follow_up?: string | null
}

export interface UpdateConsultationData {
  status?: ConsultationStatus
  clinical_notes?: string | null
  assessment?: string | null
  diagnosis?: string | null
  treatment_plan?: string | null
  follow_up?: string | null
}