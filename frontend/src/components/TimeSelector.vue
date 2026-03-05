<template>
  <div>
    <label for="time" class="block text-sm font-medium text-gray-700">전송 시간</label>
    <input
      id="time"
      v-model="timeValue"
      type="time"
      required
      class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
      @change="$emit('update:modelValue', timeValue)"
    />
    <p class="mt-1 text-sm text-gray-500">Asia/Seoul 시간대 기준</p>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const timeValue = ref(props.modelValue)

watch(() => props.modelValue, (newValue) => {
  timeValue.value = newValue
})

watch(timeValue, (newValue) => {
  emit('update:modelValue', newValue)
})
</script>
