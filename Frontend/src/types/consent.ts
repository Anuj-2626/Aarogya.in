export type ConsentStatus =
  | 'pending'
  | 'granted'
  | 'withdrawn'

export interface Consent {
  consent_id: number
  session_id: number
  consent_type: string
  status: ConsentStatus
  granted_at?: string | null
  revoked_at?: string | null
}