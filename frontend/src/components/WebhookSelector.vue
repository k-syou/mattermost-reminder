<template>
  <div>
    <label for="webhook" class="block text-sm font-medium text-gray-700">웹훅 선택</label>
    <select
      id="webhook"
      v-model="selectedUrl"
      required
      class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
      @change="$emit('update:modelValue', selectedUrl)"
    >
      <option value="">웹훅을 선택하세요</option>
      <option v-for="webhook in webhooks" :key="webhook.id" :value="webhook.url">
        {{ webhook.alias }} ({{ webhook.url }})
      </option>
    </select>
    <p v-if="webhooks.length === 0" class="mt-1 text-sm text-red-600">
      등록된 웹훅이 없습니다. <router-link to="/webhooks" class="text-indigo-600 hover:text-indigo-900">웹훅을 먼저 등록하세요.</router-link>
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useWebhookStore } from '@/stores/webhook'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const webhookStore = useWebhookStore()
const selectedUrl = ref(props.modelValue)

const webhooks = computed(() => webhookStore.webhooks)

watch(() => props.modelValue, (newValue) => {
  selectedUrl.value = newValue
})

watch(selectedUrl, (newValue) => {
  emit('update:modelValue', newValue)
})
</script>
