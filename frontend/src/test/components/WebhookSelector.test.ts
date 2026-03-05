import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import WebhookSelector from '@/components/WebhookSelector.vue'
import { useWebhookStore } from '@/stores/webhook'
import type { Webhook } from '@/types/webhook'

describe('WebhookSelector', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders webhook select', () => {
    const wrapper = mount(WebhookSelector, {
      props: {
        modelValue: ''
      },
      global: {
        stubs: {
          'router-link': true
        }
      }
    })

    const select = wrapper.find('select')
    expect(select.exists()).toBe(true)
  })

  it('displays webhooks from store', () => {
    const pinia = createPinia()
    setActivePinia(pinia)
    const webhookStore = useWebhookStore()
    
    const mockWebhooks: Webhook[] = [
      {
        id: '1',
        userId: 'user1',
        alias: 'Test Webhook',
        url: 'https://example.com/webhook',
        createdAt: new Date(),
        updatedAt: new Date()
      },
      {
        id: '2',
        userId: 'user1',
        alias: 'Another Webhook',
        url: 'https://example.com/webhook2',
        createdAt: new Date(),
        updatedAt: new Date()
      }
    ]

    webhookStore.webhooks = mockWebhooks

    const wrapper = mount(WebhookSelector, {
      props: {
        modelValue: ''
      },
      global: {
        plugins: [pinia],
        stubs: {
          'router-link': true
        }
      }
    })

    const options = wrapper.findAll('option')
    expect(options.length).toBe(3) // 기본 옵션 + 2개 웹훅
    expect(options[1].text()).toContain('Test Webhook')
    expect(options[2].text()).toContain('Another Webhook')
  })

  it('displays selected webhook', () => {
    const pinia = createPinia()
    setActivePinia(pinia)
    const webhookStore = useWebhookStore()
    
    const mockWebhooks: Webhook[] = [
      {
        id: '1',
        userId: 'user1',
        alias: 'Test Webhook',
        url: 'https://example.com/webhook',
        createdAt: new Date(),
        updatedAt: new Date()
      }
    ]

    webhookStore.webhooks = mockWebhooks

    const wrapper = mount(WebhookSelector, {
      props: {
        modelValue: 'https://example.com/webhook'
      },
      global: {
        plugins: [pinia],
        stubs: {
          'router-link': true
        }
      }
    })

    const select = wrapper.find('select')
    expect((select.element as HTMLSelectElement).value).toBe('https://example.com/webhook')
  })

  it('emits update:modelValue when webhook is selected', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)
    const webhookStore = useWebhookStore()
    
    const mockWebhooks: Webhook[] = [
      {
        id: '1',
        userId: 'user1',
        alias: 'Test Webhook',
        url: 'https://example.com/webhook',
        createdAt: new Date(),
        updatedAt: new Date()
      }
    ]

    webhookStore.webhooks = mockWebhooks

    const wrapper = mount(WebhookSelector, {
      props: {
        modelValue: ''
      },
      global: {
        plugins: [pinia],
        stubs: {
          'router-link': true
        }
      }
    })

    const select = wrapper.find('select')
    await select.setValue('https://example.com/webhook')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['https://example.com/webhook'])
  })

  it('shows error message when no webhooks available', () => {
    const pinia = createPinia()
    setActivePinia(pinia)
    const webhookStore = useWebhookStore()
    webhookStore.webhooks = []

    const wrapper = mount(WebhookSelector, {
      props: {
        modelValue: ''
      },
      global: {
        plugins: [pinia],
        stubs: {
          'router-link': true
        }
      }
    })

    const errorMessage = wrapper.find('p.text-red-600')
    expect(errorMessage.exists()).toBe(true)
    expect(errorMessage.text()).toContain('등록된 웹훅이 없습니다')
  })

  it('updates when modelValue prop changes', async () => {
    const pinia = createPinia()
    setActivePinia(pinia)
    const webhookStore = useWebhookStore()
    
    const mockWebhooks: Webhook[] = [
      {
        id: '1',
        userId: 'user1',
        alias: 'Test Webhook',
        url: 'https://example.com/webhook',
        createdAt: new Date(),
        updatedAt: new Date()
      }
    ]

    webhookStore.webhooks = mockWebhooks

    const wrapper = mount(WebhookSelector, {
      props: {
        modelValue: ''
      },
      global: {
        plugins: [pinia],
        stubs: {
          'router-link': true
        }
      }
    })

    await wrapper.setProps({ modelValue: 'https://example.com/webhook' })

    const select = wrapper.find('select')
    expect((select.element as HTMLSelectElement).value).toBe('https://example.com/webhook')
  })
})
