import { usePatient } from '@/contexts/PatientContext'
import {
  translations,
  type SupportedLanguage,
} from '@/i18n/translations'

export function useTranslation() {
  const { language } = usePatient()

  const currentLanguage: SupportedLanguage =
    language in translations ? language : 'en'

  const t = translations[currentLanguage]

  return {
    t,
    language: currentLanguage,
  }
}