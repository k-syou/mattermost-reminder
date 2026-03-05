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
              <router-link to="/webhooks" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">웹훅 관리</router-link>
              <router-link to="/messages" class="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">메시지 관리</router-link>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-bold text-gray-900">메시지 관리</h2>
          <button
            @click="showModal = true"
            class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
          >
            메시지 추가
          </button>
        </div>

        <div v-if="messageStore.error" class="mb-4 rounded-md bg-red-50 p-4">
          <div class="text-sm text-red-800">{{ messageStore.error }}</div>
        </div>

        <div v-if="messageStore.loading" class="text-center py-8">
          <span class="text-gray-500">로딩 중...</span>
        </div>

        <div v-else-if="messageStore.messages.length === 0" class="text-center py-8">
          <p class="text-gray-500 mb-4">등록된 메시지가 없습니다.</p>
          <button
            @click="showModal = true"
            class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
          >
            첫 메시지 추가하기
          </button>
        </div>

        <div v-else class="bg-white shadow overflow-hidden sm:rounded-md">
          <ul class="divide-y divide-gray-200">
            <li v-for="message in messageStore.messages" :key="message.id" class="px-6 py-4">
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center">
                    <p class="text-sm font-medium text-gray-900">{{ message.content }}</p>
                    <span
                      :class="message.isActive
                        ? 'ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800'
                        : 'ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800'"
                    >
                      {{ message.isActive ? '활성' : '비활성' }}
                    </span>
                  </div>
                  <div class="mt-2 text-sm text-gray-500">
                    <p>요일: {{ formatDaysOfWeek(message.daysOfWeek) }}</p>
                    <p>시간: {{ message.sendTime }}</p>
                    <p class="break-all">웹훅: {{ message.webhookUrl }}</p>
                  </div>
                  <p class="text-xs text-gray-400 mt-2">
                    생성일: {{ new Date(message.createdAt).toLocaleString('ko-KR') }}
                  </p>
                </div>
                <div class="ml-4 flex flex-col space-y-2">
                  <button
                    @click="toggleActive(message)"
                    :class="message.isActive
                      ? 'text-yellow-600 hover:text-yellow-900'
                      : 'text-green-600 hover:text-green-900'"
                    class="text-sm font-medium"
                  >
                    {{ message.isActive ? '비활성화' : '활성화' }}
                  </button>
                  <button
                    @click="sendNow(message.id)"
                    class="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
                  >
                    즉시 전송
                  </button>
                  <button
                    @click="editMessage(message)"
                    class="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
                  >
                    수정
                  </button>
                  <button
                    @click="deleteMessage(message.id)"
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
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
          <form @submit.prevent="handleSubmit">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
                {{ editingMessage ? '메시지 수정' : '메시지 추가' }}
              </h3>
              <div class="space-y-4">
                <div>
                  <label for="content" class="block text-sm font-medium text-gray-700">메시지 내용</label>
                  <textarea
                    id="content"
                    v-model="form.content"
                    rows="4"
                    required
                    class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="Markdown 형식 지원"
                  />
                </div>
                <DaySelector v-model="form.daysOfWeek" />
                <TimeSelector v-model="form.sendTime" />
                <WebhookSelector v-model="form.webhookUrl" />
                <div class="flex items-center">
                  <input
                    id="isActive"
                    v-model="form.isActive"
                    type="checkbox"
                    class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <label for="isActive" class="ml-2 block text-sm text-gray-900">
                    활성화
                  </label>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button
                type="submit"
                :disabled="messageStore.loading || form.daysOfWeek.length === 0"
                class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50"
              >
                {{ messageStore.loading ? '처리 중...' : (editingMessage ? '수정' : '추가') }}
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
import { useMessageStore } from '@/stores/message'
import { useWebhookStore } from '@/stores/webhook'
import DaySelector from '@/components/DaySelector.vue'
import TimeSelector from '@/components/TimeSelector.vue'
import WebhookSelector from '@/components/WebhookSelector.vue'
import { formatDaysOfWeek } from '@/utils/format'
import type { Message } from '@/types/message'

const messageStore = useMessageStore()
const webhookStore = useWebhookStore()

const showModal = ref(false)
const editingMessage = ref<Message | null>(null)

const form = reactive({
  content: '',
  daysOfWeek: [] as number[],
  sendTime: '',
  webhookUrl: '',
  isActive: true
})

const closeModal = () => {
  showModal.value = false
  editingMessage.value = null
  form.content = ''
  form.daysOfWeek = []
  form.sendTime = ''
  form.webhookUrl = ''
  form.isActive = true
}

const editMessage = (message: Message) => {
  editingMessage.value = message
  form.content = message.content
  form.daysOfWeek = [...message.daysOfWeek]
  form.sendTime = message.sendTime
  form.webhookUrl = message.webhookUrl
  form.isActive = message.isActive
  showModal.value = true
}

const handleSubmit = async () => {
  try {
    if (editingMessage.value) {
      await messageStore.updateMessage(editingMessage.value.id, form)
    } else {
      await messageStore.createMessage(form)
    }
    closeModal()
  } catch (error) {
    console.error('Message operation failed:', error)
  }
}

const deleteMessage = async (id: string) => {
  if (!confirm('정말 삭제하시겠습니까?')) return
  
  try {
    await messageStore.deleteMessage(id)
  } catch (error) {
    console.error('Delete failed:', error)
  }
}

const toggleActive = async (message: Message) => {
  try {
    await messageStore.updateMessage(message.id, { isActive: !message.isActive })
  } catch (error) {
    console.error('Toggle failed:', error)
  }
}

const sendNow = async (id: string) => {
  if (!confirm('지금 즉시 전송하시겠습니까?')) return
  
  try {
    await messageStore.sendMessageNow(id)
    alert('메시지가 전송되었습니다.')
  } catch (error) {
    console.error('Send failed:', error)
    alert('메시지 전송에 실패했습니다.')
  }
}

onMounted(async () => {
  try {
    await Promise.all([
      messageStore.fetchMessages(),
      webhookStore.fetchWebhooks()
    ])
  } catch (error) {
    console.error('Failed to load data:', error)
  }
})
</script>
