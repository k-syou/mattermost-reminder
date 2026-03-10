<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <div class="flex-shrink-0 flex items-center gap-2">
              <router-link to="/" class="flex items-center gap-2">
                <img src="/logo.png" alt="Mattermost Reminder" class="h-8 w-8 object-contain" />
                <span class="text-xl font-bold text-gray-900">Mattermost Reminder</span>
              </router-link>
            </div>
            <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
              <router-link to="/" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">대시보드</router-link>
              <router-link to="/webhooks" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">웹훅 관리</router-link>
              <router-link to="/messages" class="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">메시지 관리</router-link>
            </div>
          </div>
          <div class="flex items-center">
            <span class="text-sm text-gray-700 mr-4">{{ authStore.user?.email }}</span>
            <button
              type="button"
              @click="handleLogout"
              class="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              로그아웃
            </button>
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
                    <p>반복: {{ message.repeatCycle === 'daily' ? '매일' : '매주 ' + formatDaysOfWeek(message.daysOfWeek) }}</p>
                    <p>시간: {{ (message.sendTimes && message.sendTimes.length) ? message.sendTimes.join(', ') : message.sendTime }}</p>
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

        <!-- 전송 이력 -->
        <div v-if="!messageStore.loading" class="mt-8 bg-white shadow overflow-hidden sm:rounded-md">
          <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h3 class="text-lg font-medium text-gray-900">전송 이력</h3>
            <button
              type="button"
              @click="messageStore.fetchSendLogs()"
              class="text-sm text-indigo-600 hover:text-indigo-800"
            >
              새로고침
            </button>
          </div>
          <div v-if="messageStore.sendLogs.length === 0" class="px-6 py-8 text-center text-gray-500 text-sm">
            스케줄 또는 즉시 전송한 내역이 없습니다.
          </div>
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">전송 시각</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">메시지 ID</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">상태</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">내용 미리보기</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">오류</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="log in messageStore.sendLogs" :key="log.id" class="text-sm">
                  <td class="px-4 py-2 text-gray-600">{{ new Date(log.sentAt).toLocaleString('ko-KR') }}</td>
                  <td class="px-4 py-2 font-mono text-gray-700">{{ log.messageId }}</td>
                  <td class="px-4 py-2">
                    <span
                      :class="log.status === 'success'
                        ? 'inline-flex px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800'
                        : 'inline-flex px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800'"
                    >
                      {{ log.status === 'success' ? '성공' : '실패' }}
                    </span>
                  </td>
                  <td class="px-4 py-2 text-gray-600 max-w-xs truncate">{{ log.contentPreview || '-' }}</td>
                  <td class="px-4 py-2 text-red-600 max-w-xs truncate" :title="log.error">{{ log.error || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
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
                  <div class="flex items-center justify-between">
                    <label for="content" class="block text-sm font-medium text-gray-700">메시지 내용</label>
                    <div class="flex items-center gap-3">
                      <button
                        type="button"
                        @click="showTemplateGuideModal = true"
                        class="text-sm text-gray-600 hover:text-gray-900 font-medium"
                      >
                        템플릿 가이드
                      </button>
                      <button
                        type="button"
                        @click="showAIModal = true"
                        class="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
                      >
                        AI에게 질문하기
                      </button>
                    </div>
                  </div>
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
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">반복 주기</label>
                  <select
                    v-model="form.repeatCycle"
                    class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  >
                    <option value="weekly">매주 (요일 선택 기준)</option>
                    <option value="daily">매일</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">전송 시간</label>
                  <div class="flex gap-2 items-end">
                    <TimeSelector v-model="form.sendTime" class="flex-1" />
                    <button
                      type="button"
                      @click="addSendTime"
                      class="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                    >
                      시간 추가
                    </button>
                  </div>
                  <div v-if="form.sendTimes.length > 0" class="mt-2 flex flex-wrap gap-2">
                    <span
                      v-for="(t, i) in form.sendTimes"
                      :key="i"
                      class="inline-flex items-center gap-1 px-2 py-1 rounded bg-gray-100 text-sm"
                    >
                      {{ t }}
                      <button type="button" @click="removeSendTime(i)" class="text-gray-500 hover:text-red-600">&times;</button>
                    </span>
                  </div>
                  <p class="mt-1 text-sm text-gray-500">여러 시간을 추가하면 해당 시간마다 전송됩니다. Asia/Seoul 기준.</p>
                </div>
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
                :disabled="messageStore.loading || (form.repeatCycle === 'weekly' && form.daysOfWeek.length === 0)"
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

    <MessageTemplateGuideModal v-model="showTemplateGuideModal" />

    <!-- AI 질문 모달 -->
    <div v-if="showAIModal" class="fixed z-20 inset-0 overflow-y-auto" @click.self="showAIModal = false">
      <div class="flex items-center justify-center min-h-screen p-4">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        <div class="relative bg-white rounded-lg shadow-xl max-w-lg w-full p-6">
          <h4 class="text-lg font-medium text-gray-900 mb-3">AI에게 질문하기</h4>
          <p class="text-sm text-gray-500 mb-3">
            원하는 메시지나 요일·시간을 말하면 마크다운 내용과 설정을 추천합니다.
          </p>
          <textarea
            v-model="aiPrompt"
            rows="4"
            class="mb-4 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            placeholder="예: 매주 월수금 오전 9시에 팀 회의 리마인더 알려줘"
          />
          <div v-if="aiError" class="mb-3 text-sm text-red-600">{{ aiError }}</div>
          <div class="flex justify-end gap-2">
            <button
              type="button"
              @click="showAIModal = false; aiPrompt = ''; aiError = ''"
              class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              취소
            </button>
            <button
              type="button"
              :disabled="aiLoading || !aiPrompt.trim()"
              class="px-4 py-2 rounded-md text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
              @click="applyAIGenerate"
            >
              {{ aiLoading ? '생성 중...' : '생성' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessageStore } from '@/stores/message'
import { useWebhookStore } from '@/stores/webhook'
import { useAuthStore } from '@/stores/auth'
import DaySelector from '@/components/DaySelector.vue'
import TimeSelector from '@/components/TimeSelector.vue'
import WebhookSelector from '@/components/WebhookSelector.vue'
import MessageTemplateGuideModal from '@/components/MessageTemplateGuideModal.vue'
import { formatDaysOfWeek } from '@/utils/format'
import type { Message } from '@/types/message'

const router = useRouter()
const messageStore = useMessageStore()
const webhookStore = useWebhookStore()
const authStore = useAuthStore()

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

const showModal = ref(false)
const showAIModal = ref(false)
const showTemplateGuideModal = ref(false)
const aiPrompt = ref('')
const aiLoading = ref(false)
const aiError = ref('')
const editingMessage = ref<Message | null>(null)

const form = reactive({
  content: '',
  daysOfWeek: [] as number[],
  sendTime: '09:00',
  sendTimes: [] as string[],
  repeatCycle: 'weekly' as 'daily' | 'weekly',
  webhookUrl: '',
  isActive: true
})

const addSendTime = () => {
  if (form.sendTime && !form.sendTimes.includes(form.sendTime)) {
    form.sendTimes.push(form.sendTime)
  }
}

const removeSendTime = (index: number) => {
  form.sendTimes.splice(index, 1)
}

const closeModal = () => {
  showModal.value = false
  editingMessage.value = null
  form.content = ''
  form.daysOfWeek = []
  form.sendTime = '09:00'
  form.sendTimes = []
  form.repeatCycle = 'weekly'
  form.webhookUrl = ''
  form.isActive = true
}

const editMessage = (message: Message) => {
  editingMessage.value = message
  form.content = message.content
  form.daysOfWeek = [...message.daysOfWeek]
  form.sendTime = message.sendTime
  form.sendTimes = message.sendTimes?.length ? [...message.sendTimes] : []
  form.repeatCycle = message.repeatCycle || 'weekly'
  form.webhookUrl = message.webhookUrl
  form.isActive = message.isActive
  showModal.value = true
}

const handleSubmit = async () => {
  try {
    const allTimes = form.sendTimes.length ? form.sendTimes : [form.sendTime]
    const payload = {
      content: form.content,
      daysOfWeek: form.repeatCycle === 'daily' ? [0, 1, 2, 3, 4, 5, 6] : form.daysOfWeek,
      sendTime: allTimes[0],
      sendTimes: allTimes,
      repeatCycle: form.repeatCycle,
      webhookUrl: form.webhookUrl,
      isActive: form.isActive
    }
    if (editingMessage.value) {
      await messageStore.updateMessage(editingMessage.value.id, payload)
    } else {
      await messageStore.createMessage(payload)
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

const applyAIGenerate = async () => {
  const prompt = aiPrompt.value.trim()
  if (!prompt) return
  aiError.value = ''
  aiLoading.value = true
  try {
    const res = await messageStore.generateFromAI(prompt)
    form.content = res.content
    if (res.daysOfWeek && res.daysOfWeek.length > 0) {
      form.daysOfWeek = res.daysOfWeek
    }
    if (res.sendTime) {
      form.sendTime = res.sendTime
    }
    showAIModal.value = false
    aiPrompt.value = ''
  } catch (e: any) {
    aiError.value = e?.message || 'AI 생성에 실패했습니다.'
  } finally {
    aiLoading.value = false
  }
}

onMounted(async () => {
  try {
    await Promise.all([
      messageStore.fetchMessages(),
      webhookStore.fetchWebhooks(),
      messageStore.fetchSendLogs()
    ])
  } catch (error) {
    console.error('Failed to load data:', error)
  }
})
</script>
