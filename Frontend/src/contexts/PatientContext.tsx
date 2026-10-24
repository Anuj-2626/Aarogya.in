import {
  createContext,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import type { Patient } from '@/types/patient'
import type { Session } from '@/types/session'
import type { Consent } from '@/types/consent'
import type { SupportedLanguage } from '@/i18n/translations'

interface PatientContextValue {
  patient: Patient | null
  session: Session | null
  consent: Consent | null
  language: SupportedLanguage
  setPatient: (patient: Patient | null) => void
  setSession: (session: Session | null) => void
  setConsent: (consent: Consent | null) => void
  setLanguage: (language: SupportedLanguage) => void
  clearPatientData: () => void
}

interface PatientProviderProps {
  children: ReactNode
}

const PatientContext = createContext<PatientContextValue | undefined>(
  undefined,
)

export function PatientProvider({
  children,
}: PatientProviderProps) {
  const [patient, setPatient] = useState<Patient | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [consent, setConsent] = useState<Consent | null>(null)
  const [language, setLanguage] =
    useState<SupportedLanguage>('en')

  const clearPatientData = () => {
    setPatient(null)
    setSession(null)
    setConsent(null)
    setLanguage('en')
  }

  const value = useMemo(
    () => ({
      patient,
      session,
      consent,
      language,
      setPatient,
      setSession,
      setConsent,
      setLanguage,
      clearPatientData,
    }),
    [patient, session, consent, language],
  )

  return (
    <PatientContext.Provider value={value}>
      {children}
    </PatientContext.Provider>
  )
}

export function usePatient() {
  const context = useContext(PatientContext)

  if (!context) {
    throw new Error(
      'usePatient must be used within a PatientProvider',
    )
  }

  return context
}