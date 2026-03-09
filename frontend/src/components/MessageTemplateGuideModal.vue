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
          <h3 class="text-lg font-semibold text-gray-900">날짜/시간 템플릿 가이드</h3>
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

        <div class="flex-1 overflow-y-auto px-6 py-4 space-y-5">
          <p class="text-sm text-gray-700">
            메시지 본문에 <code class="font-mono bg-gray-100 px-1 py-0.5 rounded">{...}</code> 형식으로 날짜/시간 패턴을
            넣으면, <span class="font-medium">전송 시점(Asia/Seoul)</span>의 날짜/시간으로 자동 치환됩니다.
          </p>

          <div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
            <p class="text-sm font-medium text-gray-900 mb-2">예시</p>
            <div class="space-y-2 text-sm">
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <code class="font-mono">오늘은 {yyyy-MM-dd HH:mm} 입니다.</code>
                <span class="text-gray-600 sm:text-right">→ 2026-03-09 16:05</span>
              </div>
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <code class="font-mono">오늘은 {M/d}</code>
                <span class="text-gray-600 sm:text-right">→ 3/9</span>
              </div>
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <code class="font-mono">오늘은 {MM/dd}</code>
                <span class="text-gray-600 sm:text-right">→ 03/09</span>
              </div>
            </div>
          </div>

          <div class="rounded-lg border border-gray-200 p-4">
            <p class="text-sm font-medium text-gray-900 mb-2">지원 토큰</p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
              <div class="flex items-center justify-between">
                <code class="font-mono">yyyy</code><span class="text-gray-600">연(4자리)</span>
              </div>
              <div class="flex items-center justify-between">
                <code class="font-mono">MM</code><span class="text-gray-600">월(2자리)</span>
              </div>
              <div class="flex items-center justify-between">
                <code class="font-mono">dd</code><span class="text-gray-600">일(2자리)</span>
              </div>
              <div class="flex items-center justify-between">
                <code class="font-mono">HH</code><span class="text-gray-600">시(24h, 2자리)</span>
              </div>
              <div class="flex items-center justify-between">
                <code class="font-mono">mm</code><span class="text-gray-600">분(2자리)</span>
              </div>
              <div class="flex items-center justify-between">
                <code class="font-mono">M / d / H / m</code><span class="text-gray-600">0패딩 없음</span>
              </div>
            </div>
          </div>

          <div class="text-xs text-gray-500">
            <p>- 한 메시지에 여러 개의 <code class="font-mono">{...}</code>를 넣어도 됩니다.</p>
            <p>- 인식 불가능한 패턴은 그대로 유지됩니다.</p>
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
defineProps<{ modelValue: boolean }>()
defineEmits<{ (e: 'update:modelValue', value: boolean): void }>()
</script>

