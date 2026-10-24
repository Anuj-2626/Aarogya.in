import type { SupportedLanguage } from '@/types/session'

export interface Patient {
  patient_id: number

  name: string

  date_of_birth?: string | null

  gender?: string | null

  phone?: string | null

  preferred_language?: SupportedLanguage | null

  created_at?: string

  updated_at?: string
}
