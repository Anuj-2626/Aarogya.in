import api from './api'

import type {
  LoginResponse,
  User,
} from '@/types/auth'

export const authService = {
  login: async (
    username: string,
    password: string,
  ): Promise<LoginResponse> => {
    const formData = new URLSearchParams()

    formData.append('username', username)
    formData.append('password', password)

    const response = await api.post<LoginResponse>(
      '/auth/login',
      formData,
      {
        headers: {
          'Content-Type':
            'application/x-www-form-urlencoded',
        },
      },
    )

    return response.data
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>(
      '/auth/me',
    )

    return response.data
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout')
  },
}