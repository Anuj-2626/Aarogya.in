import { Check, Languages } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import PageContainer from '@/components/shared/PageContainer'
import { usePatient } from '@/contexts/PatientContext'
import { sessionService } from '@/services/sessionService'
import {
  useTranslation,
} from '@/i18n/useTranslation.ts'
import type { SupportedLanguage } from '@/i18n/translations'

interface LanguageOption {
  code: SupportedLanguage
  name: string
  nativeName: string
}

const languages: LanguageOption[] = [
  {
    code: 'en',
    name: 'English',
    nativeName: 'English',
  },
  {
    code: 'hi',
    name: 'Hindi',
    nativeName: 'हिन्दी',
  },
  {
    code: 'mr',
    name: 'Marathi',
    nativeName: 'मराठी',
  },
]

function LanguageSelection() {
  const navigate = useNavigate()

  const {
    session,
    setSession,
    setLanguage,
  } = usePatient()

  const { t } = useTranslation()

  const [selectedLanguage, setSelectedLanguage] =
    useState<SupportedLanguage | null>(
      session?.language ?? null,
    )

  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleContinue = async () => {
    if (!selectedLanguage) {
      setError(t.language.selectRequired)
      return
    }

    if (!session) {
      setError(t.language.sessionNotFound)
      return
    }

    setError(null)
    setIsSaving(true)

    try {
      const updatedSession =
        await sessionService.updateSession(
          session.session_id,
          {
            language: selectedLanguage,
          },
        )

      setSession(updatedSession)
      setLanguage(selectedLanguage)

      navigate('/patient/interview')
    } catch (requestError) {
      console.error(
        'Failed to update session language:',
        requestError,
      )

      setError(t.language.saveFailed)
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <main className="min-h-screen">
      <PageContainer>
        <div className="mx-auto flex max-w-2xl flex-col py-10">
          <div className="text-center">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-muted">
              <Languages className="h-7 w-7" />
            </div>

            <h1 className="mt-5 text-3xl font-bold tracking-tight">
              {t.language.title}
            </h1>

            <p className="mx-auto mt-3 max-w-lg text-muted-foreground">
              {t.language.description}
            </p>
          </div>

          <div className="mt-8 grid gap-3">
            {languages.map((language) => {
              const isSelected =
                selectedLanguage === language.code

              return (
                <button
                  key={language.code}
                  type="button"
                  onClick={() => {
                    setSelectedLanguage(language.code)
                    setLanguage(language.code)
                    setError(null)
                  }}
                  className={[
                    'flex w-full items-center justify-between rounded-xl border p-4 text-left transition-colors',
                    'hover:bg-muted/50',
                    isSelected
                      ? 'border-primary bg-primary/5'
                      : 'border-border',
                  ].join(' ')}
                  aria-pressed={isSelected}
                >
                  <div>
                    <p className="font-medium">
                      {language.name}
                    </p>

                    <p className="mt-1 text-sm text-muted-foreground">
                      {language.nativeName}
                    </p>
                  </div>

                  {isSelected && (
                    <div className="flex h-7 w-7 items-center justify-center rounded-full bg-primary text-primary-foreground">
                      <Check className="h-4 w-4" />
                    </div>
                  )}
                </button>
              )
            })}
          </div>

          {error && (
            <div
              role="alert"
              className="mt-5 rounded-lg border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive"
            >
              {error}
            </div>
          )}

          <Button
            type="button"
            className="mt-6 w-full"
            disabled={isSaving}
            onClick={handleContinue}
          >
            {isSaving
              ? t.language.saving
              : t.language.continueToInterview}
          </Button>
        </div>
      </PageContainer>
    </main>
  )
}

export default LanguageSelection