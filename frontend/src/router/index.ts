import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { auth } from '@/config/firebase'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/webhooks',
    name: 'webhooks',
    component: () => import('@/views/WebhookView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/messages',
    name: 'messages',
    component: () => import('@/views/MessageView.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Router guard for authentication
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  // Wait for Firebase Auth to restore session from localStorage
  // Firebase Auth persists session automatically, but onAuthStateChanged is async
  // Check auth.currentUser directly (synchronous) or wait for onAuthStateChanged
  if (auth.currentUser === null && authStore.user === null) {
    // Wait for auth state to be restored (max 2 seconds)
    await new Promise<void>((resolve) => {
      const timeout = setTimeout(() => resolve(), 2000)
      const unsubscribe = auth.onAuthStateChanged(() => {
        clearTimeout(timeout)
        unsubscribe()
        resolve()
      })
    })
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router
