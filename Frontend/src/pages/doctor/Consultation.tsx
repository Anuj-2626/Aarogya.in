import {
  useEffect,
  useState,
} from 'react'

import {
  ArrowLeft,
  ClipboardCheck,
  FileText,
  HeartPulse,
  Loader2,
  Save,
  Stethoscope,
} from 'lucide-react'

import {
  useNavigate,
  useParams,
} from 'react-router-dom'

import { Button } from '@/components/ui/button'

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

import { Input } from '@/components/ui/input'

import { Label } from '@/components/ui/label'

import { Textarea } from '@/components/ui/textarea'

import { patientService } from '@/services/patientService'
import { sessionService } from '@/services/sessionService'
import { consultationService } from '@/services/consultationService'

import type { Patient } from '@/types/patient'
import type { Session } from '@/types/session'
import type { Consultation as ConsultationType } from '@/types/consultation'


function Consultation() {
  const navigate = useNavigate()

  const { sessionId } = useParams<{
    sessionId: string
  }>()

  const numericSessionId = Number(sessionId)

  const [patient, setPatient] =
    useState<Patient | null>(null)

  const [session, setSession] =
    useState<Session | null>(null)

  const [consultation, setConsultation] =
    useState<ConsultationType | null>(null)

  const [clinicalNotes, setClinicalNotes] =
    useState('')

  const [assessment, setAssessment] =
    useState('')

  const [diagnosis, setDiagnosis] =
    useState('')

  const [treatmentPlan, setTreatmentPlan] =
    useState('')

  const [followUp, setFollowUp] =
    useState('')

  const [isLoading, setIsLoading] =
    useState(true)

  const [isSaving, setIsSaving] =
    useState(false)

  const [isCompleting, setIsCompleting] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)

  const [successMessage, setSuccessMessage] =
    useState<string | null>(null)


  useEffect(() => {
    if (
      !Number.isInteger(numericSessionId) ||
      numericSessionId <= 0
    ) {
      setError(
        'Invalid consultation session.',
      )
      setIsLoading(false)
      return
    }

    let mounted = true

    const loadConsultation = async () => {
      try {
        setIsLoading(true)
        setError(null)

        const loadedSession =
          await sessionService.getSession(
            numericSessionId,
          )

        if (!mounted) return

        setSession(loadedSession)

        const loadedPatient =
          await patientService.getPatient(
            loadedSession.patient_id,
          )

        if (!mounted) return

        setPatient(loadedPatient)

        const consultationResponse =
          await consultationService
            .getSessionConsultations(
              numericSessionId,
            )

        if (!mounted) return

        const existingConsultation =
          consultationResponse.consultations.find(
            (item) =>
              item.status === 'draft',
          ) ??
          consultationResponse.consultations[0] ??
          null

        setConsultation(
          existingConsultation,
        )

        if (existingConsultation) {
          setClinicalNotes(
            existingConsultation.clinical_notes ??
              '',
          )

          setAssessment(
            existingConsultation.assessment ??
              '',
          )

          setDiagnosis(
            existingConsultation.diagnosis ??
              '',
          )

          setTreatmentPlan(
            existingConsultation.treatment_plan ??
              '',
          )

          setFollowUp(
            existingConsultation.follow_up ??
              '',
          )
        }
      } catch {
        if (!mounted) return

        setError(
          'Unable to load the consultation workspace.',
        )
      } finally {
        if (mounted) {
          setIsLoading(false)
        }
      }
    }

    void loadConsultation()

    return () => {
      mounted = false
    }
  }, [numericSessionId])


  const consultationData = {
    session_id: numericSessionId,
    clinical_notes:
      clinicalNotes.trim() || null,
    assessment:
      assessment.trim() || null,
    diagnosis:
      diagnosis.trim() || null,
    treatment_plan:
      treatmentPlan.trim() || null,
    follow_up:
      followUp.trim() || null,
  }


  const handleSaveDraft = async () => {
    try {
      setIsSaving(true)
      setError(null)
      setSuccessMessage(null)

      if (consultation) {
        const updated =
          await consultationService
            .updateConsultation(
              consultation.consultation_id,
              {
                clinical_notes:
                  consultationData.clinical_notes,
                assessment:
                  consultationData.assessment,
                diagnosis:
                  consultationData.diagnosis,
                treatment_plan:
                  consultationData.treatment_plan,
                follow_up:
                  consultationData.follow_up,
              },
            )

        setConsultation(updated)
      } else {
        const created =
          await consultationService
            .createConsultation(
              consultationData,
            )

        setConsultation(created)
      }

      setSuccessMessage(
        'Consultation draft saved successfully.',
      )
    } catch {
      setError(
        'Unable to save the consultation. Please try again.',
      )
    } finally {
      setIsSaving(false)
    }
  }


  const handleComplete = async () => {
    if (
      !clinicalNotes.trim() &&
      !assessment.trim() &&
      !diagnosis.trim() &&
      !treatmentPlan.trim() &&
      !followUp.trim()
    ) {
      setError(
        'Please enter at least one clinical detail before completing the consultation.',
      )

      return
    }

    try {
      setIsCompleting(true)
      setError(null)
      setSuccessMessage(null)

      let consultationId =
        consultation?.consultation_id

      if (!consultationId) {
        const created =
          await consultationService
            .createConsultation(
              consultationData,
            )

        consultationId =
          created.consultation_id

        setConsultation(created)
      }

      const completed =
        await consultationService
          .completeConsultation(
            consultationId,
            {
              clinical_notes:
                consultationData.clinical_notes,
              assessment:
                consultationData.assessment,
              diagnosis:
                consultationData.diagnosis,
              treatment_plan:
                consultationData.treatment_plan,
              follow_up:
                consultationData.follow_up,
            },
          )

      setConsultation(completed)

      setSuccessMessage(
        'Consultation completed successfully.',
      )
    } catch {
      setError(
        'Unable to complete the consultation. Please try again.',
      )
    } finally {
      setIsCompleting(false)
    }
  }


  const handleBack = () => {
    if (patient) {
      navigate(
        `/doctor/patients/${patient.patient_id}`,
      )

      return
    }

    navigate('/doctor/dashboard')
  }


  if (isLoading) {
    return (
      <main className="mx-auto flex min-h-[70vh] max-w-5xl items-center justify-center px-4 py-8">
        <div className="flex items-center gap-3 text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />

          <span>
            Loading consultation workspace...
          </span>
        </div>
      </main>
    )
  }


  if (error && !session) {
    return (
      <main className="mx-auto max-w-5xl px-4 py-8">
        <Card>
          <CardHeader>
            <CardTitle>
              Consultation unavailable
            </CardTitle>

            <CardDescription>
              {error}
            </CardDescription>
          </CardHeader>

          <CardContent>
            <Button
              variant="outline"
              onClick={() =>
                navigate('/doctor/dashboard')
              }
            >
              Return to dashboard
            </Button>
          </CardContent>
        </Card>
      </main>
    )
  }


  return (
    <main className="mx-auto max-w-6xl px-4 py-8">
      <div className="space-y-6">

        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={handleBack}
              aria-label="Back"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>

            <div>
              <div className="flex items-center gap-2">
                <Stethoscope className="h-5 w-5 text-primary" />

                <h1 className="text-2xl font-bold tracking-tight">
                  Doctor Consultation
                </h1>
              </div>

              <p className="text-sm text-muted-foreground">
                Record the clinical assessment and management plan.
              </p>
            </div>
          </div>

          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleSaveDraft}
              disabled={
                isSaving ||
                isCompleting ||
                consultation?.status ===
                  'completed'
              }
            >
              {isSaving ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Save className="mr-2 h-4 w-4" />
              )}

              Save draft
            </Button>

            <Button
              onClick={handleComplete}
              disabled={
                isSaving ||
                isCompleting ||
                consultation?.status ===
                  'completed'
              }
            >
              {isCompleting ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <ClipboardCheck className="mr-2 h-4 w-4" />
              )}

              Complete consultation
            </Button>
          </div>
        </div>


        {error && (
          <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3">
            <p className="text-sm text-destructive">
              {error}
            </p>
          </div>
        )}


        {successMessage && (
          <div className="rounded-lg border border-green-500/30 bg-green-500/10 px-4 py-3">
            <p className="text-sm text-green-700 dark:text-green-400">
              {successMessage}
            </p>
          </div>
        )}


        {consultation?.status === 'completed' && (
          <div className="rounded-lg border border-primary/30 bg-primary/5 px-4 py-3">
            <div className="flex items-center gap-2">
              <ClipboardCheck className="h-4 w-4 text-primary" />

              <p className="text-sm font-medium">
                This consultation has been completed.
              </p>
            </div>
          </div>
        )}


        <div className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">

          <div className="space-y-6">

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <HeartPulse className="h-5 w-5" />

                  Patient
                </CardTitle>
              </CardHeader>

              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground">
                    Name
                  </p>

                  <p className="font-medium">
                    {patient?.name ?? 'Unknown patient'}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-muted-foreground">
                    Patient ID
                  </p>

                  <p className="font-medium">
                    {patient?.patient_id ?? '—'}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-muted-foreground">
                    Gender
                  </p>

                  <p className="font-medium">
                    {patient?.gender || 'Not recorded'}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-muted-foreground">
                    Phone
                  </p>

                  <p className="font-medium">
                    {patient?.phone || 'Not recorded'}
                  </p>
                </div>
              </CardContent>
            </Card>


            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />

                  Session
                </CardTitle>
              </CardHeader>

              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground">
                    Session ID
                  </p>

                  <p className="font-medium">
                    {session?.session_id ?? '—'}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-muted-foreground">
                    Session type
                  </p>

                  <p className="font-medium">
                    {session?.session_type ||
                      'Clinical intake'}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-muted-foreground">
                    Language
                  </p>

                  <p className="font-medium uppercase">
                    {session?.language || 'en'}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-muted-foreground">
                    Session status
                  </p>

                  <p className="font-medium capitalize">
                    {session?.status || '—'}
                  </p>
                </div>
              </CardContent>
            </Card>

          </div>


          <Card>
            <CardHeader>
              <CardTitle>
                Clinical Documentation
              </CardTitle>

              <CardDescription>
                Record your clinical findings, assessment, diagnosis and management decisions.
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-6">

              <div className="space-y-2">
                <Label htmlFor="clinical-notes">
                  Clinical Notes
                </Label>

                <Textarea
                  id="clinical-notes"
                  value={clinicalNotes}
                  onChange={(event) =>
                    setClinicalNotes(
                      event.target.value,
                    )
                  }
                  placeholder="Document relevant clinical findings, examination notes and observations..."
                  className="min-h-32 resize-y"
                  disabled={
                    consultation?.status ===
                    'completed'
                  }
                />
              </div>


              <div className="space-y-2">
                <Label htmlFor="assessment">
                  Assessment
                </Label>

                <Textarea
                  id="assessment"
                  value={assessment}
                  onChange={(event) =>
                    setAssessment(
                      event.target.value,
                    )
                  }
                  placeholder="Enter your clinical assessment..."
                  className="min-h-28 resize-y"
                  disabled={
                    consultation?.status ===
                    'completed'
                  }
                />
              </div>


              <div className="space-y-2">
                <Label htmlFor="diagnosis">
                  Diagnosis
                </Label>

                <Input
                  id="diagnosis"
                  value={diagnosis}
                  onChange={(event) =>
                    setDiagnosis(
                      event.target.value,
                    )
                  }
                  placeholder="Enter diagnosis or provisional diagnosis..."
                  disabled={
                    consultation?.status ===
                    'completed'
                  }
                />
              </div>


              <div className="space-y-2">
                <Label htmlFor="treatment-plan">
                  Treatment / Management Plan
                </Label>

                <Textarea
                  id="treatment-plan"
                  value={treatmentPlan}
                  onChange={(event) =>
                    setTreatmentPlan(
                      event.target.value,
                    )
                  }
                  placeholder="Document medicines, procedures, lifestyle advice or other management decisions..."
                  className="min-h-32 resize-y"
                  disabled={
                    consultation?.status ===
                    'completed'
                  }
                />
              </div>


              <div className="space-y-2">
                <Label htmlFor="follow-up">
                  Follow-up / Recommendations
                </Label>

                <Textarea
                  id="follow-up"
                  value={followUp}
                  onChange={(event) =>
                    setFollowUp(
                      event.target.value,
                    )
                  }
                  placeholder="Enter follow-up date, monitoring instructions or recommendations..."
                  className="min-h-28 resize-y"
                  disabled={
                    consultation?.status ===
                    'completed'
                  }
                />
              </div>

            </CardContent>
          </Card>

        </div>

      </div>
    </main>
  )
}


export default Consultation