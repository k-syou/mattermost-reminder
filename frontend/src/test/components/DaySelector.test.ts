import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DaySelector from '@/components/DaySelector.vue'

describe('DaySelector', () => {
  it('renders all days of the week', () => {
    const wrapper = mount(DaySelector, {
      props: {
        modelValue: []
      }
    })

    // 요일 선택 label들만 찾기 (에러 메시지 label 제외)
    const dayLabels = wrapper.findAll('label.inline-flex')
    expect(dayLabels.length).toBe(7) // 일, 월, 화, 수, 목, 금, 토
  })

  it('displays selected days', () => {
    const wrapper = mount(DaySelector, {
      props: {
        modelValue: [1, 3, 5] // 월, 수, 금
      }
    })

    const inputs = wrapper.findAll('input[type="checkbox"]')
    expect((inputs[1].element as HTMLInputElement).checked).toBe(true) // 월
    expect((inputs[3].element as HTMLInputElement).checked).toBe(true) // 수
    expect((inputs[5].element as HTMLInputElement).checked).toBe(true) // 금
  })

  it('emits update:modelValue when day is toggled', async () => {
    const wrapper = mount(DaySelector, {
      props: {
        modelValue: [1, 3]
      }
    })

    const inputs = wrapper.findAll('input[type="checkbox"]')
    await inputs[0].setValue(true) // 일 추가

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    const emitted = wrapper.emitted('update:modelValue')?.[0]
    expect(emitted?.[0]).toContain(0) // 일이 포함되어야 함
  })

  it('shows error message when no days are selected', () => {
    const wrapper = mount(DaySelector, {
      props: {
        modelValue: []
      }
    })

    const errorMessage = wrapper.find('p.text-red-600')
    expect(errorMessage.exists()).toBe(true)
    expect(errorMessage.text()).toContain('최소 하나의 요일을 선택해야 합니다')
  })

  it('hides error message when days are selected', () => {
    const wrapper = mount(DaySelector, {
      props: {
        modelValue: [1]
      }
    })

    const errorMessage = wrapper.find('p.text-red-600')
    expect(errorMessage.exists()).toBe(false)
  })

  it('updates when modelValue prop changes', async () => {
    const wrapper = mount(DaySelector, {
      props: {
        modelValue: [1]
      }
    })

    await wrapper.setProps({ modelValue: [1, 2, 3] })

    const inputs = wrapper.findAll('input[type="checkbox"]')
    expect((inputs[1].element as HTMLInputElement).checked).toBe(true)
    expect((inputs[2].element as HTMLInputElement).checked).toBe(true)
    expect((inputs[3].element as HTMLInputElement).checked).toBe(true)
  })
})
