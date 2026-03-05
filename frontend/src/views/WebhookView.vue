<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <div class="flex-shrink-0 flex items-center">
              <router-link to="/" class="text-xl font-bold text-gray-900">Mattermost Reminder</router-link>
            </div>
            <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
              <router-link to="/" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">대시보드</router-link>
              <router-link to="/webhooks" class="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">웹훅 관리</router-link>
              <router-link to="/messages" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">메시지 관리</router-link>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-gray-900">웹훅 관리</h2>
          <button
            @click="showModal = true"
            class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
          >
            웹훅 추가
          </button>
        </div>

        <div v-if="webhookStore.error" class="mb-4 rounded-md bg-red-50 p-4">
          <div class="text-sm text-red-800">{{ webhookStore.error }}</div>
        </div>

        <div v-if="webhookStore.loading" class="text-center py-8">
          <span class="text-gray-500">로딩 중...</span>
        </div>

        <div v-else-if="webhookStore.webhooks.length === 0" class="text-center py-8">
          <p class="text-gray-500 mb-4">등록된 웹훅이 없습니다.</p>
          <button
            @click="showModal = true"
            class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
          >
            첫 웹훅 추가하기
          </button>
        </div>

        <div v-else class="bg-white shadow overflow-hidden sm:rounded-md">
          <ul class="divide-y divide-gray-200">
            <li v-for="webhook in webhookStore.webhooks" :key="webhook.id" class="px-6 py-4">
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <div class="flex items-center">
                    <p class="text-sm font-medium text-gray-900">{{ webhook.alias }}</p>
                  </div>
                  <p class="text-sm text-gray-500 mt-1 break-all">{{ webhook.url }}</p>
                  <p class="text-xs text-gray-400 mt-1">
                    생성일: {{ new Date(webhook.createdAt).toLocaleString('ko-KR') }}
                  </p>
                </div>
                <div class="ml-4 flex space-x-2">
                  <button
                    @click="editWebhook(webhook)"
                    class="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
                  >
                    수정
                  </button>
                  <button
                    @click="deleteWebhook(webhook.id)"
                    class="text-red-600 hover:text-red-900 text-sm font-medium"
                  >
                    삭제
                  </button>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </main>

    <!-- Add/Edit Modal -->
    <div v-if="showModal" class="fixed z-10 inset-0 overflow-y-auto" @click.self="closeModal">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <form @submit.prevent="handleSubmit">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
                {{ editingWebhook ? '웹훅 수정' : '웹훅 추가' }}
              </h3>
              <div class="space-y-4">
                <div>
                  <label for="alias" class="block text-sm font-medium text-gray-700">별칭</label>
                  <input
                    id="alias"
                    v-model="form.alias"
                    type="text"
                    required
                    class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="예: 개발팀 채널"
                  />
                </div>
                <div>
                  <label for="url" class="block text-sm font-medium text-gray-700">웹훅 URL</label>
                  <input
                    id="url"
                    v-model="form.url"
                    type="url"
                    required
                    class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="https://..."
                  />
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button
                type="submit"
                :disabled="webhookStore.loading"
                class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50"
              >
                {{ webhookStore.loading ? '처리 중...' : (editingWebhook ? '수정' : '추가') }}
              </button>
              <button
                type="button"
                @click="closeModal"
                class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
              >
                취소
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useWebhookStore } from '@/stores/webhook'
import type { Webhook } from '@/types/webhook'

const webhookStore = useWebhookStore()

const showModal = ref(false)
const editingWebhook = ref<Webhook | null>(null)

const form = reactive({
  alias: '',
  url: ''
})

const closeModal = () => {
  showModal.value = false
  editingWebhook.value = null
  form.alias = ''
  form.url = ''
}

const editWebhook = (webhook: Webhook) => {
  editingWebhook.value = webhook
  form.alias = webhook.alias
  form.url = webhook.url
  showModal.value = true
}

const handleSubmit = async () => {
  try {
    if (editingWebhook.value) {
      await webhookStore.updateWebhook(editingWebhook.value.id, form.alias, form.url)
    } else {
      await webhookStore.createWebhook(form.alias, form.url)
    }
    closeModal()
  } catch (error) {
    console.error('Webhook operation failed:', error)
  }
}

const deleteWebhook = async (id: string) => {
  if (!confirm('정말 삭제하시겠습니까?')) return
  
  try {
    await webhookStore.deleteWebhook(id)
  } catch (error) {
    console.error('Delete failed:', error)
  }
}

onMounted(async () => {
  try {
    await webhookStore.fetchWebhooks()
  } catch (error) {
    console.error('Failed to load webhooks:', error)
  }
})
</script>
