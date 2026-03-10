import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'
import type { Message, SendLog, MessageAIGenerateResponse } from '@/types/message'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export const useMessageStore = defineStore('message', () => {
  const messages = ref<Message[]>([])
  const sendLogs = ref<SendLog[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const authStore = useAuthStore()

  const fetchMessages = async () => {
    try {
      loading.value = true
      error.value = null
      const token = await authStore.getIdToken()
      if (!token) throw new Error('인증 토큰이 없습니다.')

      const response = await fetch(`${API_BASE_URL}/api/messages`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) throw new Error('메시지 목록을 불러오는데 실패했습니다.')
      messages.value = await response.json()
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const createMessage = async (data: {
    content: string
    daysOfWeek: number[]
    sendTime: string
    sendTimes?: string[]
    repeatCycle?: 'daily' | 'weekly'
    sendOnce?: boolean
    timeRangeStart?: string
    timeRangeEnd?: string
    intervalSeconds?: number
    webhookUrl: string
    isActive?: boolean
  }) => {
    try {
      loading.value = true
      error.value = null
      const token = await authStore.getIdToken()
      if (!token) throw new Error('인증 토큰이 없습니다.')

      const response = await fetch(`${API_BASE_URL}/api/messages`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      })

      if (!response.ok) throw new Error('메시지 생성에 실패했습니다.')
      const newMessage = await response.json()
      messages.value.push(newMessage)
      return newMessage
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateMessage = async (id: string, data: Partial<{
    content: string
    daysOfWeek: number[]
    sendTime: string
    sendTimes: string[]
    repeatCycle: 'daily' | 'weekly'
    sendOnce: boolean
    timeRangeStart: string
    timeRangeEnd: string
    intervalSeconds: number
    webhookUrl: string
    isActive: boolean
  }>) => {
    try {
      loading.value = true
      error.value = null
      const token = await authStore.getIdToken()
      if (!token) throw new Error('인증 토큰이 없습니다.')

      const response = await fetch(`${API_BASE_URL}/api/messages/${id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      })

      if (!response.ok) throw new Error('메시지 수정에 실패했습니다.')
      const updatedMessage = await response.json()
      const index = messages.value.findIndex(m => m.id === id)
      if (index !== -1) {
        messages.value[index] = updatedMessage
      }
      return updatedMessage
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteMessage = async (id: string) => {
    try {
      loading.value = true
      error.value = null
      const token = await authStore.getIdToken()
      if (!token) throw new Error('인증 토큰이 없습니다.')

      const response = await fetch(`${API_BASE_URL}/api/messages/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) throw new Error('메시지 삭제에 실패했습니다.')
      messages.value = messages.value.filter(m => m.id !== id)
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const sendMessageNow = async (id: string) => {
    try {
      loading.value = true
      error.value = null
      const token = await authStore.getIdToken()
      if (!token) throw new Error('인증 토큰이 없습니다.')

      const response = await fetch(`${API_BASE_URL}/api/messages/${id}/send`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) throw new Error('메시지 전송에 실패했습니다.')
      const result = await response.json()
      await fetchSendLogs()
      return result
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchSendLogs = async (limit = 100) => {
    try {
      const token = await authStore.getIdToken()
      if (!token) return

      const response = await fetch(
        `${API_BASE_URL}/api/messages/send-logs?limit=${limit}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      )
      if (!response.ok) return
      sendLogs.value = await response.json()
    } catch {
      sendLogs.value = []
    }
  }

  const generateFromAI = async (prompt: string): Promise<MessageAIGenerateResponse> => {
    const token = await authStore.getIdToken()
    if (!token) throw new Error('인증 토큰이 없습니다.')

    const response = await fetch(`${API_BASE_URL}/api/messages/ai-generate`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ prompt })
    })

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(err.detail || 'AI 생성에 실패했습니다.')
    }
    return response.json()
  }

  return {
    messages,
    sendLogs,
    loading,
    error,
    fetchMessages,
    createMessage,
    updateMessage,
    deleteMessage,
    sendMessageNow,
    fetchSendLogs,
    generateFromAI
  }
})
