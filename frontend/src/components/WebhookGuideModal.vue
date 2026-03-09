<template>
  <div
    v-if="modelValue"
    class="fixed z-20 inset-0 overflow-y-auto"
    aria-modal="true"
    role="dialog"
    @click.self="$emit('update:modelValue', false)"
  >
    <div class="flex min-h-full items-center justify-center p-4">
      <div class="fixed inset-0 bg-gray-900/60 transition-opacity" />
      <div
        class="relative bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] flex flex-col"
        @click.stop
      >
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-semibold text-gray-900">웹훅 등록 가이드</h3>
          <button
            type="button"
            class="rounded-md p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            aria-label="닫기"
            @click="$emit('update:modelValue', false)"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="flex-1 overflow-y-auto px-6 py-4">
          <div class="space-y-6">
            <div
              v-for="(step, index) in steps"
              :key="index"
              class="flex flex-col sm:flex-row gap-4 items-start"
            >
              <div
                class="flex-shrink-0 w-10 h-10 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-semibold"
              >
                {{ index + 1 }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 mb-2">{{ step.title }}</p>
                <img
                  :src="step.image"
                  :alt="step.title"
                  class="rounded-lg border border-gray-200 w-full max-h-80 object-contain bg-gray-50"
                />
              </div>
            </div>
          </div>
        </div>

        <div class="px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-xl">
          <button
            type="button"
            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-sm font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            @click="$emit('update:modelValue', false)"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import webhookGuide1 from '@statics/webhook_guide_1.png'
import webhookGuide2 from '@statics/webhook_guide_2.png'
import webhookGuide3 from '@statics/webhook_guide_3.png'
import webhookGuide4 from '@statics/webhook_guide_4.png'
import webhookGuide5 from '@statics/webhook_guide_5.png'
import webhookGuide6 from '@statics/webhook_guide_6.png'

defineProps<{ modelValue: boolean }>()
defineEmits<{ (e: 'update:modelValue', value: boolean): void }>()

const steps = [
  { title: 'Mattermost 앱 왼쪽 상단 메뉴 버튼을 클릭하세요.', image: webhookGuide1 },
  { title: '메뉴에서 "통합" 버튼을 클릭하세요.', image: webhookGuide2 },
  { title: '"전체 Incoming Webhook" 버튼을 클릭하세요.', image: webhookGuide3 },
  { title: '"Incoming Webhook 추가하기" 버튼을 클릭하세요.', image: webhookGuide4 },
  {
    title: '제목, 설명, 채널 등을 입력(선택)한 뒤 저장 버튼을 클릭하세요.',
    image: webhookGuide5,
  },
  { title: '생성된 URL을 복사하여 웹훅 URL로 등록하세요.', image: webhookGuide6 },
]
</script>
