import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'
import type { Webhook } from '@/types/webhook'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export const useWebhookStore = defineStore('webhook', () => {
  const webhooks = ref<Webhook[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const authStore = useAuthStore()

  const fetchWebhooks = async () => {
    try {
      loading.value = true
      error.value = null
      const token = await authStore.getIdToken()
      if (!token) throw new Error('인증 토큰이 없습니다.')

      const response = await fetch(`${API_BASE_URL}/api/webhooks`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) throw new Error('웹훅 목록을 불러오는데 실패했습니다.')
      webhooks.value = await response.json()
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const createWebhook = async (alias: string, url: string) => {
    try {
      loading.value = true
      error.value = null
      const token = await authStore.getIdToken()
      if (!token) throw new Error('인증 토큰이 없습니다.')

      const response = await fetch(`${API_BASE_URL}/api/webhooks`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ alias, url })
      })

      if (!response.ok) throw new Error('웹훅 생성에 실패했습니다.')
      const newWebhook = await response.json()
      webhooks.value.push(newWebhook)
      return newWebhook
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateWebhook = async (id: string, alias?: string, url?: string) => {
    try {
      loading.value = true
      error.value = null
      const token = await authStore.getIdToken()
      if (!token) throw new Error('인증 토큰이 없습니다.')

      const body: any = {}
      if (alias !== undefined) body.alias = alias
      if (url !== undefined) body.url = url

      const response = await fetch(`${API_BASE_URL}/api/webhooks/${id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
      })

      if (!response.ok) throw new Error('웹훅 수정에 실패했습니다.')
      const updatedWebhook = await response.json()
      const index = webhooks.value.findIndex(w => w.id === id)
      if (index !== -1) {
        webhooks.value[index] = updatedWebhook
      }
      return updatedWebhook
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteWebhook = async (id: string) => {
    try {
      loading.value = true
      error.value = null
      const token = await authStore.getIdToken()
      if (!token) throw new Error('인증 토큰이 없습니다.')

      const response = await fetch(`${API_BASE_URL}/api/webhooks/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) throw new Error('웹훅 삭제에 실패했습니다.')
      webhooks.value = webhooks.value.filter(w => w.id !== id)
    } catch (err: any) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    webhooks,
    loading,
    error,
    fetchWebhooks,
    createWebhook,
    updateWebhook,
    deleteWebhook
  }
})
