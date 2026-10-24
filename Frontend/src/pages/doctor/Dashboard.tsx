import { useEffect, useState } from 'react'
import {
  useNavigate,
} from 'react-router-dom'
import {
  AlertCircle,
  ClipboardList,
  LogOut,
  RefreshCw,
  Search,
  UserRound,
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'

import { useAuth } from '@/contexts/AuthContext'
import api from '@/services/api'

interface Patient {
  patient_id: number
  name: string
  date_of_birth: string
  gender: string
  phone: string
  preferred_language?: string | null
  created_at?: string
  updated_at?: string
}

function Dashboard() {
  const navigate = useNavigate()

  const {
    user,
    logout,
  } = useAuth()

  const [
    patients,
    setPatients,
  ] = useState<Patient[]>([])

  const [
    searchTerm,
    setSearchTerm,
  ] = useState('')

  const [
    isLoading,
    setIsLoading,
  ] = useState(true)

  const [
    error,
    setError,
  ] = useState<string | null>(null)

  const loadPatients = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response =
        await api.get<Patient[]>(
          '/patients/',
        )

      setPatients(response.data)
    } catch (requestError) {
      if (
        typeof requestError === 'object' &&
        requestError !== null &&
        'response' in requestError
      ) {
        const response = (
          requestError as {
            response?: {
              data?: {
                detail?: string
              }
            }
          }
        ).response

        setError(
          response?.data?.detail ??
            'Unable to load patients.',
        )
      } else {
        setError(
          'Unable to connect to Aarogya.in.',
        )
      }
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    void loadPatients()
  }, [])

  const handleLogout = async () => {
    await logout()

    navigate('/doctor/login', {
      replace: true,
    })
  }

  const handleViewPatient = (
    patientId: number,
  ) => {
    navigate(
      `/doctor/patients/${patientId}`,
    )
  }

  const normalizedSearch =
    searchTerm.trim().toLowerCase()

  const filteredPatients =
    patients.filter((patient) => {
      if (!normalizedSearch) {
        return true
      }

      return (
        patient.name
          .toLowerCase()
          .includes(normalizedSearch) ||
        patient.phone
          .toLowerCase()
          .includes(normalizedSearch) ||
        String(patient.patient_id)
          .includes(normalizedSearch)
      )
    })

  return (
    <main className="min-h-[calc(100vh-4rem)] bg-muted/20 px-4 py-6 md:px-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm text-muted-foreground">
              Aarogya.in
            </p>

            <h1 className="text-3xl font-bold tracking-tight">
              Doctor Dashboard
            </h1>

            <p className="mt-1 text-muted-foreground">
              Welcome, {user?.username}.
            </p>
          </div>

          <Button
            variant="outline"
            onClick={handleLogout}
          >
            <LogOut className="mr-2 h-4 w-4" />
            Sign out
          </Button>
        </header>

        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>
                Registered patients
              </CardDescription>

              <CardTitle className="flex items-center gap-2 text-3xl">
                <UserRound className="h-6 w-6" />
                {patients.length}
              </CardTitle>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardDescription>
                Doctor access
              </CardDescription>

              <CardTitle className="flex items-center gap-2 text-lg capitalize">
                <ClipboardList className="h-5 w-5" />
                {user?.role ?? 'doctor'}
              </CardTitle>
            </CardHeader>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <CardTitle>
                  Patient Queue
                </CardTitle>

                <CardDescription>
                  Select a patient to review their clinical information.
                </CardDescription>
              </div>

              <Button
                variant="outline"
                onClick={() =>
                  void loadPatients()
                }
                disabled={isLoading}
              >
                <RefreshCw
                  className={`mr-2 h-4 w-4 ${
                    isLoading
                      ? 'animate-spin'
                      : ''
                  }`}
                />
                Refresh
              </Button>
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />

              <Input
                value={searchTerm}
                onChange={(event) =>
                  setSearchTerm(
                    event.target.value,
                  )
                }
                placeholder="Search by patient name, phone, or ID..."
                className="pl-9"
              />
            </div>

            {error && (
              <div className="flex items-start gap-3 rounded-lg border border-destructive/30 bg-destructive/10 p-4">
                <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-destructive" />

                <div>
                  <p className="font-medium text-destructive">
                    Unable to load patients
                  </p>

                  <p className="mt-1 text-sm text-destructive/90">
                    {error}
                  </p>
                </div>
              </div>
            )}

            {isLoading ? (
              <div className="flex min-h-48 items-center justify-center">
                <div className="text-center">
                  <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />

                  <p className="mt-3 text-sm text-muted-foreground">
                    Loading patients...
                  </p>
                </div>
              </div>
            ) : filteredPatients.length === 0 ? (
              <div className="flex min-h-48 flex-col items-center justify-center rounded-lg border border-dashed px-6 text-center">
                <UserRound className="h-10 w-10 text-muted-foreground" />

                <h2 className="mt-3 font-semibold">
                  {patients.length === 0
                    ? 'No patients registered yet'
                    : 'No matching patients'}
                </h2>

                <p className="mt-1 max-w-md text-sm text-muted-foreground">
                  {patients.length === 0
                    ? 'Patients registered through the Aarogya.in workflow will appear here.'
                    : 'Try searching with a different name, phone number, or patient ID.'}
                </p>
              </div>
            ) : (
              <div className="divide-y rounded-lg border">
                {filteredPatients.map(
                  (patient) => (
                    <div
                      key={patient.patient_id}
                      className="flex flex-col gap-4 p-4 transition-colors hover:bg-muted/40 md:flex-row md:items-center md:justify-between"
                    >
                      <div className="flex items-start gap-3">
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10">
                          <UserRound className="h-5 w-5 text-primary" />
                        </div>

                        <div>
                          <h3 className="font-semibold">
                            {patient.name}
                          </h3>

                          <div className="mt-1 space-y-1 text-sm text-muted-foreground">
                            <p>
                              Patient ID:{' '}
                              {patient.patient_id}
                            </p>

                            <p>
                              {patient.gender} ·{' '}
                              {patient.phone}
                            </p>

                            <p>
                              Date of birth:{' '}
                              {patient.date_of_birth}
                            </p>
                          </div>
                        </div>
                      </div>

                      <Button
                        type="button"
                        onClick={() =>
                          handleViewPatient(
                            patient.patient_id,
                          )
                        }
                      >
                        View patient
                      </Button>
                    </div>
                  ),
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </main>
  )
}

export default Dashboard