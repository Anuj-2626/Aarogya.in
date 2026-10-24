export interface ExtractedMedicalData {
  diagnoses: string[]
  medications: string[]
  lab_results: string[]
  procedures: string[]
  dates: string[]
}

export type ExtractedData =
  | string
  | ExtractedMedicalData
  | null

export type OCRStatus =
  | 'pending'
  | 'processing'
  | 'completed'
  | 'failed'
  | string

export interface MedicalDocument {
  document_id: number
  session_id: number
  filename: string
  file_type: string
  storage_path?: string
  ocr_text?: string | null
  ocr_status: OCRStatus
  extracted_data: ExtractedData
  document_date?: string | null
  created_at: string
}

export interface UploadMedicalDocumentResponse
  extends MedicalDocument {}

export interface ProcessMedicalDocumentResponse
  extends MedicalDocument {}