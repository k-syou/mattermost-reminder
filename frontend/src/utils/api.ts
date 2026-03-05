import { useAuthStore } from '@/stores/auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export async function apiRequest(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const authStore = useAuthStore()
  const token = await authStore.getIdToken()

  if (!token) {
    throw new Error('인증 토큰이 없습니다.')
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers
    }
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '요청에 실패했습니다.' }))
    throw new Error(error.detail || error.message || '요청에 실패했습니다.')
  }

  return response
}
