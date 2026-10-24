
import {
  ArrowRight,
  FileText,
  Loader2,
  Upload,
  X,
} from 'lucide-react'
import {
  useEffect,
  useRef,
  useState,
  type ChangeEvent,
} from 'react'
import { useNavigate } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

import PageContainer from '@/components/shared/PageContainer'

import { usePatient } from '@/contexts/PatientContext'
import { documentService } from '@/services/documentService'

import type { MedicalDocument } from '@/types/document'

const MAX_FILE_SIZE = 10 * 1024 * 1024

const ALLOWED_FILE_TYPES = [
  'application/pdf',
  'image/jpeg',
  'image/png',
]

const ALLOWED_EXTENSIONS = [
  '.pdf',
  '.jpg',
  '.jpeg',
  '.png',
]

interface FastAPIValidationError {
  type?: string
  loc?: unknown[]
  msg?: string
  input?: unknown
}

function getErrorMessage(
  error: unknown,
): string {
  if (
    typeof error !== 'object' ||
    error === null ||
    !('response' in error)
  ) {
    return 'Unable to connect to Aarogya.in. Please try again.'
  }

  const response = (
    error as {
      response?: {
        data?: {
          detail?:
            | string
            | FastAPIValidationError[]
        }
      }
    }
  ).response

  const detail = response?.data?.detail

  if (typeof detail === 'string') {
    return detail
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => item.msg)
      .filter(
        (message): message is string =>
          Boolean(message),
      )

    if (messages.length > 0) {
      return messages.join(' ')
    }
  }

  return 'The medical document upload request was rejected. Please try again.'
}

function Documents() {
  const navigate = useNavigate()
  const { session } = usePatient()

  const fileInputRef =
    useRef<HTMLInputElement | null>(null)

  const [selectedFile, setSelectedFile] =
    useState<File | null>(null)

  const [documents, setDocuments] = useState<
    MedicalDocument[]
  >([])

  const [isLoadingDocuments, setIsLoadingDocuments] =
    useState(true)

  const [isUploading, setIsUploading] =
    useState(false)

  const [processingDocumentId, setProcessingDocumentId] =
    useState<number | null>(null)

  const [error, setError] =
    useState<string | null>(null)

  const [successMessage, setSuccessMessage] =
    useState<string | null>(null)

  useEffect(() => {
    const loadDocuments = async () => {
      if (!session) {
        setError(
          'Your clinical intake session could not be found. Please restart the patient registration process.',
        )

        setIsLoadingDocuments(false)

        return
      }

      try {
        setError(null)

        const existingDocuments =
          await documentService.getSessionDocuments(
            Number(session.session_id),
          )

        setDocuments(existingDocuments)
      } catch (requestError) {
        console.error(
          'Failed to load medical documents:',
          requestError,
        )

        /*
         * Document retrieval is optional.
         *
         * Even if the document service is temporarily
         * unavailable, the patient must still be able
         * to continue with the clinical intake.
         */
        setError(getErrorMessage(requestError))
      } finally {
        setIsLoadingDocuments(false)
      }
    }

    void loadDocuments()
  }, [session])

  const handleFileChange = (
    event: ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0]

    if (!file) {
      return
    }

    setError(null)
    setSuccessMessage(null)

    if (file.size > MAX_FILE_SIZE) {
      setSelectedFile(null)

      setError(
        'File size must be 10 MB or less.',
      )

      event.target.value = ''

      return
    }

    const fileName = file.name.toLowerCase()

    const hasAllowedMimeType =
      ALLOWED_FILE_TYPES.includes(file.type)

    const hasAllowedExtension =
      ALLOWED_EXTENSIONS.some((extension) =>
        fileName.endsWith(extension),
      )

    if (
      !hasAllowedMimeType &&
      !hasAllowedExtension
    ) {
      setSelectedFile(null)

      setError(
        'Please select a PDF, JPG, JPEG, or PNG medical document.',
      )

      event.target.value = ''

      return
    }

    setSelectedFile(file)
  }

  const handleRemoveFile = () => {
    setSelectedFile(null)
    setError(null)
    setSuccessMessage(null)

    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleUpload = async () => {
    if (!session) {
      setError(
        'Your clinical intake session could not be found. Please restart the patient registration process.',
      )

      return
    }

    if (!selectedFile) {
      setError(
        'Please select a medical document first.',
      )

      return
    }

    if (selectedFile.size > MAX_FILE_SIZE) {
      setError(
        'File size must be 10 MB or less.',
      )

      return
    }

    setError(null)
    setSuccessMessage(null)
    setIsUploading(true)

    try {
      const uploadedDocument =
        await documentService.uploadDocument(
          Number(session.session_id),
          selectedFile,
        )

      setDocuments((currentDocuments) => [
        ...currentDocuments,
        uploadedDocument,
      ])

      setSelectedFile(null)

      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

      setSuccessMessage(
        'Medical document uploaded successfully. Starting OCR processing...',
      )

      setProcessingDocumentId(
        uploadedDocument.document_id,
      )

      try {
        const processedDocument =
          await documentService.processDocument(
            uploadedDocument.document_id,
          )

        setDocuments((currentDocuments) =>
          currentDocuments.map((document) =>
            document.document_id ===
            processedDocument.document_id
              ? processedDocument
              : document,
          ),
        )

        setSuccessMessage(
          'Medical document uploaded and processed successfully.',
        )
      } catch (ocrError) {
        /*
         * OCR is an optional enhancement.
         *
         * A failed OCR operation must NOT block the
         * patient from continuing through the workflow.
         */
        console.error(
          'OCR processing failed:',
          ocrError,
        )

        setSuccessMessage(
          'Medical document uploaded, but OCR processing could not be completed. You can still continue.',
        )

        setError(null)
      }
    } catch (requestError) {
      console.error(
        'Failed to upload medical document:',
        requestError,
      )

      /*
       * Upload itself failed. This is shown to the
       * patient, but the Continue button remains
       * available because documents are optional.
       */
      setError(getErrorMessage(requestError))
    } finally {
      setIsUploading(false)
      setProcessingDocumentId(null)
    }
  }

  const getOCRStatusLabel = (
    status: MedicalDocument['ocr_status'],
  ) => {
    switch (status) {
      case 'pending':
        return 'Pending'

      case 'processing':
        return 'Processing'

      case 'completed':
        return 'Processed'

      case 'failed':
        return 'Processing failed'

      default:
        return status
    }
  }

  const handleContinue = () => {
    navigate('/patient/timeline')
  }

  return (
    <main className="min-h-[calc(100vh-4rem)] px-4 py-8">
      <PageContainer>
        <div className="mx-auto w-full max-w-3xl space-y-6">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              Medical Documents
            </h1>

            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              Upload previous medical reports,
              prescriptions, lab reports, or other
              relevant documents.
            </p>

            <p className="mt-2 text-sm font-medium text-muted-foreground">
              This step is optional. You can skip it and
              continue to your medical timeline.
            </p>
          </div>

          {error && (
            <div className="rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3">
              <p className="text-sm text-destructive">
                {error}
              </p>
            </div>
          )}

          {successMessage && (
            <div className="rounded-md border border-primary/30 bg-primary/10 px-4 py-3">
              <p className="text-sm">
                {successMessage}
              </p>
            </div>
          )}

          <Card>
            <CardHeader>
              <CardTitle>
                Upload Medical Document
              </CardTitle>

              <CardDescription>
                PDF, JPG, JPEG, or PNG files up to 10
                MB. Uploading a document is optional.
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-5">
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.jpg,.jpeg,.png,application/pdf,image/jpeg,image/png"
                onChange={handleFileChange}
                className="hidden"
              />

              <button
                type="button"
                onClick={() =>
                  fileInputRef.current?.click()
                }
                disabled={isUploading}
                className="flex w-full cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 text-center transition hover:bg-muted/50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <Upload className="mb-3 h-8 w-8 text-muted-foreground" />

                <p className="font-medium">
                  Select a medical document
                </p>

                <p className="mt-1 text-sm text-muted-foreground">
                  Click here to choose a file
                </p>
              </button>

              {selectedFile && (
                <div className="rounded-lg border bg-muted/30 p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex min-w-0 items-start gap-3">
                      <FileText className="mt-0.5 h-5 w-5 shrink-0 text-primary" />

                      <div className="min-w-0">
                        <p className="truncate text-sm font-medium">
                          {selectedFile.name}
                        </p>

                        <p className="mt-1 text-xs text-muted-foreground">
                          {(
                            selectedFile.size /
                            (1024 * 1024)
                          ).toFixed(2)}{' '}
                          MB
                        </p>
                      </div>
                    </div>

                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={handleRemoveFile}
                      disabled={isUploading}
                      aria-label="Remove selected file"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )}

              <Button
                type="button"
                className="w-full"
                disabled={
                  !selectedFile ||
                  isUploading ||
                  !session
                }
                onClick={() => void handleUpload()}
              >
                {isUploading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />

                    {processingDocumentId !== null
                      ? 'Processing document...'
                      : 'Uploading document...'}
                  </>
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" />

                    Upload Document
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>
                Uploaded Documents
              </CardTitle>

              <CardDescription>
                Medical documents associated with this
                clinical session.
              </CardDescription>
            </CardHeader>

            <CardContent>
              {isLoadingDocuments ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />

                  <span className="ml-2 text-sm text-muted-foreground">
                    Loading documents...
                  </span>
                </div>
              ) : documents.length === 0 ? (
                <div className="rounded-lg border border-dashed p-8 text-center">
                  <FileText className="mx-auto mb-3 h-8 w-8 text-muted-foreground" />

                  <p className="font-medium">
                    No documents uploaded yet
                  </p>

                  <p className="mt-1 text-sm text-muted-foreground">
                    You can continue without uploading a
                    medical document.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {documents.map((document) => (
                    <div
                      key={document.document_id}
                      className="rounded-lg border p-4"
                    >
                      <div className="flex items-start gap-3">
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-primary/10">
                          <FileText className="h-5 w-5 text-primary" />
                        </div>

                        <div className="min-w-0 flex-1">
                          <p className="truncate text-sm font-medium">
                            {document.filename}
                          </p>

                          <div className="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-xs text-muted-foreground">
                            <span>
                              {document.file_type}
                            </span>

                            <span>
                              OCR:{' '}
                              {getOCRStatusLabel(
                                document.ocr_status,
                              )}
                            </span>
                          </div>

                          {document.ocr_text && (
                            <div className="mt-3 rounded-md bg-muted/40 p-3">
                              <p className="text-xs font-medium">
                                OCR Text
                              </p>

                              <p className="mt-1 whitespace-pre-wrap text-sm leading-6 text-muted-foreground">
                                {document.ocr_text}
                              </p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <div className="flex flex-col gap-3 border-t pt-5 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-muted-foreground">
              Medical documents are optional. You can
              continue without uploading anything.
            </p>

            <Button
              type="button"
              onClick={handleContinue}
              disabled={isUploading}
              className="w-full sm:w-auto"
            >
              Continue to Medical Timeline
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      </PageContainer>
    </main>
  )
}

export default Documents

