import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  type User
} from 'firebase/auth'
import { auth } from '@/config/firebase'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => user.value !== null)

  // Initialize auth state listener
  onAuthStateChanged(auth, (firebaseUser) => {
    user.value = firebaseUser
  })

  const login = async (email: string, password: string) => {
    try {
      loading.value = true
      error.value = null
      await signInWithEmailAndPassword(auth, email, password)
    } catch (err: any) {
      error.value = err.message || '로그인에 실패했습니다.'
      throw err
    } finally {
      loading.value = false
    }
  }

  const register = async (email: string, password: string) => {
    try {
      loading.value = true
      error.value = null
      await createUserWithEmailAndPassword(auth, email, password)
    } catch (err: any) {
      error.value = err.message || '회원가입에 실패했습니다.'
      throw err
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      loading.value = true
      error.value = null
      await signOut(auth)
    } catch (err: any) {
      error.value = err.message || '로그아웃에 실패했습니다.'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getIdToken = async (): Promise<string | null> => {
    if (!user.value) return null
    try {
      return await user.value.getIdToken()
    } catch (err) {
      console.error('Failed to get ID token:', err)
      return null
    }
  }

  return {
    user,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    getIdToken
  }
})
