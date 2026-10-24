export interface Interview {
  interview_id: number
  session_id: number
  interview_type: string
  status: 'not_started' | 'in_progress' | 'completed'
  current_question_id: number | null
  language: 'en' | 'hi' | 'mr' | 'bn' | 'ta'
  started_at: string | null
  completed_at: string | null
  created_at: string
}

export interface Question {
  question_id: number
  interview_id: number
  question_code: string
  question_text: string
  question_type: string
  history_section: string
  sequence_number: number
  is_required: boolean
  parent_question_id: number | string | null
  language: 'en' | 'hi' | 'mr' | 'bn' | 'ta'
  created_at: string
}

export interface Answer {
  answer_id: number
  interview_id: number
  question_id: number
  answer_text: string
  answer_type: string
  answered_at: string
}