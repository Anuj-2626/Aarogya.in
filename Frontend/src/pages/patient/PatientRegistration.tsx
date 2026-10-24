import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { CalendarDays, Phone, UserRound } from 'lucide-react'

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

import { usePatient } from '@/contexts/PatientContext'
import { patientService } from '@/services/patientService'
import { sessionService } from '@/services/sessionService'

const patientSchema = z.object({
  name: z
    .string()
    .trim()
    .min(2, 'Please enter the patient name.'),

  date_of_birth: z
    .string()
    .optional(),

  gender: z
    .string()
    .optional(),

  phone: z
    .string()
    .trim()
    .optional()
    .refine(
      (value) =>
        !value || /^[0-9]{10}$/.test(value),
      'Please enter a valid 10-digit phone number.',
    ),

  preferred_language: z.enum([
    'en',
    'hi',
    'mr',
  ]),
})

type PatientFormData = z.infer<typeof patientSchema>

function PatientRegistration() {
  const navigate = useNavigate()
  const { setPatient, setSession } = usePatient()

  const [serverError, setServerError] = useState<string | null>(
    null,
  )

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<PatientFormData>({
    resolver: zodResolver(patientSchema),
    defaultValues: {
      preferred_language: 'en',
    },
  })

  const onSubmit = async (data: PatientFormData) => {
    setServerError(null)

    try {
      // ---------------------------------------------------------
      // Step 1: Create patient
      // ---------------------------------------------------------

      const patient = await patientService.createPatient({
        name: data.name,
        date_of_birth: data.date_of_birth || null,
        gender: data.gender || null,
        phone: data.phone || null,
        preferred_language: data.preferred_language,
      })

      setPatient(patient)

      // ---------------------------------------------------------
      // Step 2: Create clinical intake session
      // ---------------------------------------------------------

      const session = await sessionService.createSession({
        patient_id: patient.patient_id,
        session_type: 'clinical_intake',
        language: data.preferred_language,
      })

      setSession(session)

      // ---------------------------------------------------------
      // Step 3: Continue to consent
      // ---------------------------------------------------------

      navigate('/patient/consent')
    } catch (error) {
      if (
        typeof error === 'object' &&
        error !== null &&
        'response' in error
      ) {
        const response = (
          error as {
            response?: {
              data?: {
                detail?: string
              }
            }
          }
        ).response

        setServerError(
          response?.data?.detail ??
            'Unable to continue the patient registration process. Please try again.',
        )
      } else {
        setServerError(
          'Unable to connect to Aarogya.in. Please try again.',
        )
      }
    }
  }

  return (
    <main className="min-h-[calc(100vh-4rem)] px-4 py-8">
      <div className="mx-auto flex w-full max-w-2xl items-center justify-center">
        <Card className="w-full">
          <CardHeader>
            <CardTitle className="text-2xl">
              Patient Registration
            </CardTitle>

            <CardDescription>
              Enter the patient details to begin the
              clinical intake process.
            </CardDescription>
          </CardHeader>

          <CardContent>
            <form
              onSubmit={handleSubmit(onSubmit)}
              className="space-y-5"
            >
              <div className="space-y-2">
                <Label htmlFor="name">
                  Full Name
                </Label>

                <div className="relative">
                  <UserRound className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />

                  <Input
                    id="name"
                    type="text"
                    placeholder="Enter patient's full name"
                    className="pl-9"
                    autoComplete="name"
                    {...register('name')}
                  />
                </div>

                {errors.name && (
                  <p className="text-sm text-destructive">
                    {errors.name.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="date_of_birth">
                  Date of Birth
                </Label>

                <div className="relative">
                  <CalendarDays className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />

                  <Input
                    id="date_of_birth"
                    type="date"
                    className="pl-9"
                    {...register('date_of_birth')}
                  />
                </div>

                {errors.date_of_birth && (
                  <p className="text-sm text-destructive">
                    {errors.date_of_birth.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="gender">
                  Gender
                </Label>

                <select
                  id="gender"
                  className="border-input bg-background flex h-9 w-full rounded-md border px-3 py-1 text-sm shadow-xs outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  {...register('gender')}
                >
                  <option value="">
                    Prefer not to say
                  </option>

                  <option value="male">
                    Male
                  </option>

                  <option value="female">
                    Female
                  </option>

                  <option value="other">
                    Other
                  </option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone">
                  Phone Number
                </Label>

                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />

                  <Input
                    id="phone"
                    type="tel"
                    inputMode="numeric"
                    placeholder="10-digit phone number"
                    className="pl-9"
                    autoComplete="tel"
                    maxLength={10}
                    {...register('phone')}
                  />
                </div>

                {errors.phone && (
                  <p className="text-sm text-destructive">
                    {errors.phone.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="preferred_language">
                  Preferred Language
                </Label>

                <select
                  id="preferred_language"
                  className="border-input bg-background flex h-9 w-full rounded-md border px-3 py-1 text-sm shadow-xs outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  {...register('preferred_language')}
                >
                  <option value="en">
                    English
                  </option>

                  <option value="hi">
                    Hindi
                  </option>

                  <option value="mr">
                    Marathi
                  </option>
                </select>
              </div>

              {serverError && (
                <div className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2">
                  <p className="text-sm text-destructive">
                    {serverError}
                  </p>
                </div>
              )}

              <Button
                type="submit"
                className="w-full"
                disabled={isSubmitting}
              >
                {isSubmitting
                  ? 'Starting intake...'
                  : 'Continue'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </main>
  )
}

export default PatientRegistration