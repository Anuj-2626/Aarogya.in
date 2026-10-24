export type SupportedLanguage =
  | 'en'
  | 'hi'
  | 'mr'

export interface Session {
  session_id: number

  patient_id: number

  session_type: string

  status: string

  language?: SupportedLanguage | null

  started_at?: string | null

  ended_at?: string | null

  created_at?: string

  completed_at?: string | null

  consent_status?: string | null
}
