import { useState } from 'react'
import {
  useLocation,
  useNavigate,
} from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import {
  LockKeyhole,
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
import { Label } from '@/components/ui/label'

import { useAuth } from '@/contexts/AuthContext'
import { authService } from '@/services/authService'

const loginSchema = z.object({
  username: z
    .string()
    .min(
      3,
      'Username must be at least 3 characters.',
    ),

  password: z
    .string()
    .min(
      8,
      'Password must be at least 8 characters.',
    ),
})

type LoginFormData = z.infer<typeof loginSchema>

function Login() {
  const navigate = useNavigate()
  const location = useLocation()

  const { login } = useAuth()

  const [
    serverError,
    setServerError,
  ] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: {
      errors,
      isSubmitting,
    },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  })

  const onSubmit = async (
    data: LoginFormData,
  ) => {
    setServerError(null)

    try {
      const loginResponse =
        await authService.login(
          data.username,
          data.password,
        )

      localStorage.setItem(
        'access_token',
        loginResponse.access_token,
      )

      const user =
        await authService.getCurrentUser()

      if (
        user.role !== 'doctor' &&
        user.role !== 'admin'
      ) {
        localStorage.removeItem(
          'access_token',
        )

        setServerError(
          'This account does not have access to the Doctor Portal.',
        )

        return
      }

      login(
        user,
        loginResponse.access_token,
      )

      const state = location.state as
        | {
            from?: {
              pathname?: string
            }
          }
        | null

      const destination =
        state?.from?.pathname?.startsWith(
          '/doctor/',
        )
          ? state.from.pathname
          : '/doctor/dashboard'

      navigate(destination, {
        replace: true,
      })
    } catch (error) {
      localStorage.removeItem(
        'access_token',
      )

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
            'Unable to sign in. Please check your credentials.',
        )
      } else {
        setServerError(
          'Unable to connect to Aarogya.in. Please try again.',
        )
      }
    }
  }

  return (
    <main className="flex min-h-[calc(100vh-4rem)] items-center justify-center px-4 py-8">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">
            Doctor Portal
          </CardTitle>

          <CardDescription>
            Sign in to access patient clinical information.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <form
            onSubmit={handleSubmit(onSubmit)}
            className="space-y-5"
          >
            <div className="space-y-2">
              <Label htmlFor="username">
                Username
              </Label>

              <div className="relative">
                <UserRound className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />

                <Input
                  id="username"
                  type="text"
                  placeholder="Enter your username"
                  className="pl-9"
                  autoComplete="username"
                  {...register('username')}
                />
              </div>

              {errors.username && (
                <p className="text-sm text-destructive">
                  {errors.username.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">
                Password
              </Label>

              <div className="relative">
                <LockKeyhole className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />

                <Input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  className="pl-9"
                  autoComplete="current-password"
                  {...register('password')}
                />
              </div>

              {errors.password && (
                <p className="text-sm text-destructive">
                  {errors.password.message}
                </p>
              )}
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
                ? 'Signing in...'
                : 'Sign in'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </main>
  )
}

export default Login