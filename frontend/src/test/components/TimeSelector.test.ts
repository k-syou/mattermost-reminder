import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TimeSelector from '@/components/TimeSelector.vue'

describe('TimeSelector', () => {
  it('renders time input', () => {
    const wrapper = mount(TimeSelector, {
      props: {
        modelValue: ''
      }
    })

    const input = wrapper.find('input[type="time"]')
    expect(input.exists()).toBe(true)
  })

  it('displays initial time value', () => {
    const wrapper = mount(TimeSelector, {
      props: {
        modelValue: '09:00'
      }
    })

    const input = wrapper.find('input[type="time"]')
    expect((input.element as HTMLInputElement).value).toBe('09:00')
  })

  it('emits update:modelValue when time changes', async () => {
    const wrapper = mount(TimeSelector, {
      props: {
        modelValue: '09:00'
      }
    })

    const input = wrapper.find('input[type="time"]')
    await input.setValue('14:30')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['14:30'])
  })

  it('updates when modelValue prop changes', async () => {
    const wrapper = mount(TimeSelector, {
      props: {
        modelValue: '09:00'
      }
    })

    await wrapper.setProps({ modelValue: '15:45' })

    const input = wrapper.find('input[type="time"]')
    expect((input.element as HTMLInputElement).value).toBe('15:45')
  })

  it('displays timezone information', () => {
    const wrapper = mount(TimeSelector, {
      props: {
        modelValue: '09:00'
      }
    })

    const timezoneText = wrapper.find('p.text-gray-500')
    expect(timezoneText.exists()).toBe(true)
    expect(timezoneText.text()).toContain('Asia/Seoul')
  })
})
