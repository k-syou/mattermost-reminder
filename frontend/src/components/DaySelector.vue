<template>
  <div :class="{ 'opacity-60 pointer-events-none': disabled }">
    <label class="block text-sm font-medium text-gray-700 mb-2">요일 선택</label>
    <div class="flex flex-wrap gap-2">
      <label
        v-for="day in days"
        :key="day.value"
        class="inline-flex items-center px-3 py-2 border rounded-md cursor-pointer transition-colors"
        :class="selectedDays.includes(day.value)
          ? 'bg-indigo-600 text-white border-indigo-600'
          : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'"
      >
        <input
          type="checkbox"
          :value="day.value"
          :checked="selectedDays.includes(day.value)"
          :disabled="disabled"
          @change="toggleDay(day.value)"
          class="sr-only"
        />
        <span>{{ day.label }}</span>
      </label>
    </div>
    <p v-if="!disabled && selectedDays.length === 0" class="mt-1 text-sm text-red-600">
      최소 하나의 요일을 선택해야 합니다.
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    modelValue: number[]
    disabled?: boolean
  }>(),
  { disabled: false }
)

const emit = defineEmits<{
  'update:modelValue': [value: number[]]
}>()

const days = [
  { value: 0, label: '일' },
  { value: 1, label: '월' },
  { value: 2, label: '화' },
  { value: 3, label: '수' },
  { value: 4, label: '목' },
  { value: 5, label: '금' },
  { value: 6, label: '토' }
]

const selectedDays = ref([...props.modelValue])

const toggleDay = (day: number) => {
  const index = selectedDays.value.indexOf(day)
  if (index > -1) {
    selectedDays.value.splice(index, 1)
  } else {
    selectedDays.value.push(day)
  }
  emit('update:modelValue', [...selectedDays.value])
}

watch(() => props.modelValue, (newValue) => {
  selectedDays.value = [...newValue]
}, { deep: true })
</script>
