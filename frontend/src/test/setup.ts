import { beforeEach } from 'vitest'
import { config } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

// Pinia 설정
beforeEach(() => {
  setActivePinia(createPinia())
})

// 전역 설정
config.global.stubs = {
  'router-link': true,
  'router-view': true
}
