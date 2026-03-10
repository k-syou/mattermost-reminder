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
              <div class="flex flex-col gap-2">
                <div class="flex items-start justify-between">
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center flex-wrap gap-2">
                      <p class="text-sm font-medium text-gray-900">{{ message.content.length > 30 ? message.content.slice(0, 30) + '…' : message.content }}</p>
                      <span
                        v-if="message.sendOnce"
                        class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800"
                      >
                        1회 작동
                      </span>
                    </div>
                    <div class="mt-2 text-sm text-gray-500">
                      <p>반복: {{ repeatCycleLabel(message.repeatCycle, message.daysOfWeek) }}</p>
                      <p v-if="message.timeRangeStart && message.timeRangeEnd && (message.intervalSeconds ?? 0) > 0">
                        시간: {{ message.timeRangeStart }}~{{ message.timeRangeEnd }}
                        {{ formatInterval(message.intervalSeconds!) }} 간격
                      </p>
                      <p v-else>시간: {{ (message.sendTimes && message.sendTimes.length) ? message.sendTimes.join(', ') : message.sendTime }}</p>
                      <p>웹훅: {{ getWebhookAlias(message.webhookUrl) }}</p>
                    </div>
                  </div>
                </div>
                <div class="flex items-center justify-between pt-2 border-t border-gray-100">
                  <p class="text-xs text-gray-400">
                    생성일: {{ new Date(message.createdAt).toLocaleString('ko-KR') }}
                  </p>
                  <div class="flex items-center gap-2">
                    <button
                      type="button"
                      role="switch"
                      :aria-checked="message.isActive"
                      :class="[
                        'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2',
                        message.isActive ? 'bg-indigo-600' : 'bg-gray-200'
                      ]"
                      @click="toggleActive(message)"
                    >
                      <span
                        :class="[
                          'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition',
                          message.isActive ? 'translate-x-5' : 'translate-x-0.5'
                        ]"
                      />
                    </button>
                    <button
                      type="button"
                      class="p-1.5 text-indigo-600 hover:text-indigo-800 rounded"
                      title="즉시 전송"
                      @click="sendNow(message.id)"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
                    </button>
                    <button
                      type="button"
                      class="p-1.5 text-gray-600 hover:text-gray-800 rounded"
                      title="수정"
                      @click="editMessage(message)"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                    </button>
                    <button
                      type="button"
                      class="p-1.5 text-red-600 hover:text-red-800 rounded"
                      title="삭제"
                      @click="deleteMessage(message.id)"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                    </button>
                  </div>
                </div>
              </div>
            </li>
          </ul>
        </div>

        <!-- 전송 이력 -->
        <div v-if="!messageStore.loading" class="mt-5 bg-white shadow overflow-hidden sm:rounded-md">
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
                    ref="contentTextareaRef"
                    id="content"
                    v-model="form.content"
                    rows="4"
                    required
                    class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm resize-none overflow-y-auto"
                    placeholder="Markdown 형식 지원"
                    style="min-height: 100px"
                    @input="resizeContentTextarea"
                  />
                </div>
                <DaySelector v-model="form.daysOfWeek" :disabled="form.repeatCycle === 'daily' || form.repeatCycle === 'weekdays' || form.repeatCycle === 'weekend'" />
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">반복 주기</label>
                  <select
                    v-model="form.repeatCycle"
                    class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    @change="onRepeatCycleChange"
                  >
                    <option value="weekly">매주 (요일 선택 기준)</option>
                    <option value="daily">매일</option>
                    <option value="weekdays">평일</option>
                    <option value="weekend">주말</option>
                  </select>
                  <p v-if="form.repeatCycle === 'daily'" class="mt-1 text-sm text-gray-500">매일 선택 시 모든 요일이 자동 적용됩니다.</p>
                  <p v-else-if="form.repeatCycle === 'weekdays'" class="mt-1 text-sm text-gray-500">평일(월~금)이 자동 적용됩니다.</p>
                  <p v-else-if="form.repeatCycle === 'weekend'" class="mt-1 text-sm text-gray-500">주말(토, 일)이 자동 적용됩니다.</p>
                </div>
                <div
                  class="transition-opacity"
                  :class="{ 'opacity-50 pointer-events-none': form.useTimeRangeMode }"
                >
                  <label class="block text-sm font-medium text-gray-700 mb-1">전송 시간</label>
                  <p v-if="form.useTimeRangeMode" class="text-xs text-amber-600 mb-1">특정 시간 반복을 사용 중이라 편집할 수 없습니다.</p>
                  <div class="flex gap-2 items-end">
                    <TimeSelector v-model="form.sendTime" :show-label="false" class="flex-1" />
                    <button
                      type="button"
                      :disabled="form.useTimeRangeMode"
                      @click="addSendTime"
                      class="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
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
                      <button type="button" :disabled="form.useTimeRangeMode" @click="removeSendTime(i)" class="text-gray-500 hover:text-red-600 disabled:opacity-50 disabled:cursor-not-allowed">&times;</button>
                    </span>
                  </div>
                  <p class="mt-1 text-sm text-gray-500">여러 시간을 추가하면 해당 시간마다 전송됩니다.</p>
                </div>
                <div
                  class="transition-opacity"
                  :class="{ 'opacity-50 pointer-events-none': !form.useTimeRangeMode && form.sendTimes.length > 0 }"
                >
                  <div class="flex items-center gap-2 mb-1">
                    <input
                      id="useTimeRangeMode"
                      v-model="form.useTimeRangeMode"
                      type="checkbox"
                      class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <label for="useTimeRangeMode" class="block text-sm font-medium text-gray-700">특정 시간 반복 사용</label>
                  </div>
                  <p v-if="form.useTimeRangeMode && !timeRangeValid" class="text-xs text-red-600 mb-1">
                    시작·종료 시간과 간격(시/분/초 중 최소 1초 이상)을 모두 입력해 주세요.
                  </p>
                  <p v-else-if="form.useTimeRangeMode" class="text-xs text-gray-500 mb-1">시작~종료 시간 사이를 지정한 간격마다 전송합니다. 둘 중 하나만 선택 가능합니다.</p>
                  <div v-if="form.useTimeRangeMode" class="grid grid-cols-2 sm:grid-cols-5 gap-2 items-end mt-1">
                    <div>
                      <label for="timeRangeStart" class="block text-xs text-gray-600">시작</label>
                      <input
                        id="timeRangeStart"
                        v-model="form.timeRangeStart"
                        type="time"
                        class="mt-0.5 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      />
                    </div>
                    <div>
                      <label for="timeRangeEnd" class="block text-xs text-gray-600">종료</label>
                      <input
                        id="timeRangeEnd"
                        v-model="form.timeRangeEnd"
                        type="time"
                        class="mt-0.5 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      />
                    </div>
                    <div>
                      <label for="intervalHours" class="block text-xs text-gray-600">간격 시</label>
                      <input
                        id="intervalHours"
                        v-model.number="form.intervalHours"
                        type="number"
                        min="0"
                        max="24"
                        class="mt-0.5 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        placeholder="0"
                      />
                    </div>
                    <div>
                      <label for="intervalMins" class="block text-xs text-gray-600">간격 분</label>
                      <input
                        id="intervalMins"
                        v-model.number="form.intervalMins"
                        type="number"
                        min="0"
                        max="59"
                        class="mt-0.5 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        placeholder="0"
                      />
                    </div>
                    <div>
                      <label for="intervalSecs" class="block text-xs text-gray-600">간격 초</label>
                      <input
                        id="intervalSecs"
                        v-model.number="form.intervalSecs"
                        type="number"
                        min="0"
                        max="59"
                        class="mt-0.5 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        placeholder="0"
                      />
                    </div>
                  </div>
                  <p v-if="form.useTimeRangeMode" class="mt-1 text-sm text-gray-500">Asia/Seoul 시간대 기준</p>
                </div>
                <WebhookSelector v-model="form.webhookUrl" />
                <div class="flex flex-col gap-2">
                  <div class="flex items-center">
                    <input
                      id="sendOnce"
                      v-model="form.sendOnce"
                      type="checkbox"
                      class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <label for="sendOnce" class="ml-2 block text-sm text-gray-900">
                      1회만 보내기 (전송 후 자동 비활성화)
                    </label>
                  </div>
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
            </div>
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button
                type="submit"
                :disabled="messageStore.loading || (form.repeatCycle === 'weekly' && form.daysOfWeek.length === 0) || (form.useTimeRangeMode && !timeRangeValid)"
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
import { ref, reactive, computed, watch, nextTick, onMounted } from 'vue'
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

function formatInterval(seconds: number): string {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  const parts = []
  if (h > 0) parts.push(`${h}시간`)
  if (m > 0) parts.push(`${m}분`)
  if (s > 0) parts.push(`${s}초`)
  return parts.length ? parts.join(' ') : '0초'
}

function repeatCycleLabel(cycle?: string, daysOfWeek: number[] = []): string {
  if (cycle === 'daily') return '매일'
  if (cycle === 'weekdays') return '평일'
  if (cycle === 'weekend') return '주말'
  return '매주 ' + formatDaysOfWeek(daysOfWeek)
}

function getWebhookAlias(url: string): string {
  const w = webhookStore.webhooks.find(wh => wh.url === url)
  return (w?.alias ?? url) || '—'
}

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
const contentTextareaRef = ref<HTMLTextAreaElement | null>(null)

const form = reactive({
  content: '',
  daysOfWeek: [] as number[],
  sendTime: '09:00',
  sendTimes: [] as string[],
  repeatCycle: 'weekly' as 'daily' | 'weekly' | 'weekdays' | 'weekend',
  sendOnce: false,
  useTimeRangeMode: false,
  timeRangeStart: '' as string,
  timeRangeEnd: '' as string,
  intervalHours: 0 as number,
  intervalMins: 0 as number,
  intervalSecs: 0 as number,
  webhookUrl: '',
  isActive: true
})

function resizeContentTextarea() {
  nextTick(() => {
    const el = contentTextareaRef.value
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.max(100, el.scrollHeight)}px`
  })
}

watch(() => form.content, () => resizeContentTextarea())
watch(showModal, (open) => { if (open) resizeContentTextarea() })

const timeRangeValid = computed(() => {
  const sec = (form.intervalHours || 0) * 3600 + (form.intervalMins || 0) * 60 + (form.intervalSecs || 0)
  return !!(form.timeRangeStart && form.timeRangeEnd && sec >= 1)
})

function onRepeatCycleChange() {
  if (form.repeatCycle === 'daily') form.daysOfWeek = [0, 1, 2, 3, 4, 5, 6]
  else if (form.repeatCycle === 'weekdays') form.daysOfWeek = [1, 2, 3, 4, 5]
  else if (form.repeatCycle === 'weekend') form.daysOfWeek = [0, 6]
}

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
  form.sendOnce = false
  form.useTimeRangeMode = false
  form.timeRangeStart = ''
  form.timeRangeEnd = ''
  form.intervalHours = 0
  form.intervalMins = 0
  form.intervalSecs = 0
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
  if (form.repeatCycle === 'daily') form.daysOfWeek = [0, 1, 2, 3, 4, 5, 6]
  else if (form.repeatCycle === 'weekdays') form.daysOfWeek = [1, 2, 3, 4, 5]
  else if (form.repeatCycle === 'weekend') form.daysOfWeek = [0, 6]
  form.sendOnce = message.sendOnce ?? false
  form.timeRangeStart = message.timeRangeStart ?? ''
  form.timeRangeEnd = message.timeRangeEnd ?? ''
  const total = message.intervalSeconds ?? 0
  form.intervalHours = Math.floor(total / 3600)
  form.intervalMins = Math.floor((total % 3600) / 60)
  form.intervalSecs = total % 60
  form.useTimeRangeMode = !!(message.timeRangeStart && message.timeRangeEnd && total >= 1)
  form.webhookUrl = message.webhookUrl
  form.isActive = message.isActive
  showModal.value = true
}

const handleSubmit = async () => {
  try {
    if (form.useTimeRangeMode && !timeRangeValid.value) {
      return
    }
    const intervalSeconds = (form.intervalHours || 0) * 3600 + (form.intervalMins || 0) * 60 + (form.intervalSecs || 0)
    const useRange = form.useTimeRangeMode && timeRangeValid.value
    const allTimes = useRange ? [] : (form.sendTimes.length ? form.sendTimes : [form.sendTime])
    const payload = {
      content: form.content,
      daysOfWeek: form.repeatCycle === 'daily' ? [0, 1, 2, 3, 4, 5, 6] : form.repeatCycle === 'weekdays' ? [1, 2, 3, 4, 5] : form.repeatCycle === 'weekend' ? [0, 6] : form.daysOfWeek,
      sendTime: useRange ? form.timeRangeStart : allTimes[0],
      sendTimes: allTimes,
      repeatCycle: form.repeatCycle,
      sendOnce: form.sendOnce,
      ...(useRange && {
        timeRangeStart: form.timeRangeStart,
        timeRangeEnd: form.timeRangeEnd,
        intervalSeconds
      }),
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
    if (res.timeRangeStart && res.timeRangeEnd && (res.intervalSeconds ?? 0) >= 1) {
      form.useTimeRangeMode = true
      form.timeRangeStart = res.timeRangeStart
      form.timeRangeEnd = res.timeRangeEnd
      form.intervalHours = Math.floor((res.intervalSeconds ?? 0) / 3600)
      form.intervalMins = Math.floor(((res.intervalSeconds ?? 0) % 3600) / 60)
      form.intervalSecs = (res.intervalSeconds ?? 0) % 60
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
