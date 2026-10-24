export type SafetyFlagStatus =
  | 'active'
  | 'resolved'

export interface SafetyFlag {
  safety_flag_id: number
  interview_id: number
  question_id: number
  category: string
  severity: string
  message: string
  detected_at: string
  status: SafetyFlagStatus
}