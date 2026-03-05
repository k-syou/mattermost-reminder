<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <div class="flex-shrink-0 flex items-center">
              <h1 class="text-xl font-bold text-gray-900">Mattermost Reminder</h1>
            </div>
            <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
              <router-link
                to="/"
                class="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              >
                대시보드
              </router-link>
              <router-link
                to="/webhooks"
                class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              >
                웹훅 관리
              </router-link>
              <router-link
                to="/messages"
                class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              >
                메시지 관리
              </router-link>
            </div>
          </div>
          <div class="flex items-center">
            <span class="text-sm text-gray-700 mr-4">{{ authStore.user?.email }}</span>
            <button
              @click="handleLogout"
              class="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              로그아웃
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <!-- Webhooks Card -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">등록된 웹훅</dt>
                    <dd class="text-lg font-medium text-gray-900">{{ webhookStore.webhooks.length }}개</dd>
                  </dl>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-5 py-3">
              <div class="text-sm">
                <router-link to="/webhooks" class="font-medium text-indigo-700 hover:text-indigo-900">
                  웹훅 관리하기
                </router-link>
              </div>
            </div>
          </div>

          <!-- Messages Card -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">스케줄된 메시지</dt>
                    <dd class="text-lg font-medium text-gray-900">{{ messageStore.messages.length }}개</dd>
                  </dl>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-5 py-3">
              <div class="text-sm">
                <router-link to="/messages" class="font-medium text-indigo-700 hover:text-indigo-900">
                  메시지 관리하기
                </router-link>
              </div>
            </div>
          </div>

          <!-- Active Messages Card -->
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">활성 메시지</dt>
                    <dd class="text-lg font-medium text-gray-900">
                      {{ activeMessagesCount }}개
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-5 py-3">
              <div class="text-sm text-gray-500">
                자동 전송 중
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Messages -->
        <div class="mt-8">
          <div class="bg-white shadow rounded-lg">
            <div class="px-4 py-5 sm:p-6">
              <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">최근 메시지</h3>
              <div v-if="messageStore.loading" class="text-center py-4">
                <span class="text-gray-500">로딩 중...</span>
              </div>
              <div v-else-if="recentMessages.length === 0" class="text-center py-4">
                <span class="text-gray-500">등록된 메시지가 없습니다.</span>
              </div>
              <div v-else class="space-y-4">
                <div
                  v-for="message in recentMessages"
                  :key="message.id"
                  class="border-b border-gray-200 pb-4 last:border-0 last:pb-0"
                >
                  <div class="flex items-center justify-between">
                    <div class="flex-1">
                      <p class="text-sm font-medium text-gray-900">{{ message.content }}</p>
                      <p class="text-sm text-gray-500 mt-1">
                        {{ formatDaysOfWeek(message.daysOfWeek) }} {{ message.sendTime }}
                        <span :class="message.isActive ? 'text-green-600' : 'text-gray-400'">
                          ({{ message.isActive ? '활성' : '비활성' }})
                        </span>
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useWebhookStore } from '@/stores/webhook'
import { useMessageStore } from '@/stores/message'
import { formatDaysOfWeek } from '@/utils/format'

const router = useRouter()
const authStore = useAuthStore()
const webhookStore = useWebhookStore()
const messageStore = useMessageStore()

const activeMessagesCount = computed(() => {
  return messageStore.messages.filter(m => m.isActive).length
})

const recentMessages = computed(() => {
  return messageStore.messages.slice(0, 5)
})

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

onMounted(async () => {
  try {
    await Promise.all([
      webhookStore.fetchWebhooks(),
      messageStore.fetchMessages()
    ])
  } catch (error) {
    console.error('Failed to load data:', error)
  }
})
</script>
