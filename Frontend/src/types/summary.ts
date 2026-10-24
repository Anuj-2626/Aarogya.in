export type ClinicalSummaryStatus =
  | 'generated'
  | 'failed'
  | 'outdated'

export interface ClinicalSummary {
  summary_id: number
  session_id: number
  summary_text: string
  structured_data: string | null
  source_version: string | null
  status: ClinicalSummaryStatus
  generated_at: string
  updated_at: string
}

export interface ClinicalSummaryListResponse {
  session_id: number
  summaries: ClinicalSummary[]
  total_summaries: number
}
