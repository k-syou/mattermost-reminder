import { describe, it, expect } from 'vitest'
import { formatDaysOfWeek, formatTime } from '@/utils/format'

describe('format utils', () => {
  describe('formatDaysOfWeek', () => {
    it('formats single day', () => {
      expect(formatDaysOfWeek([0])).toBe('일')
      expect(formatDaysOfWeek([1])).toBe('월')
      expect(formatDaysOfWeek([6])).toBe('토')
    })

    it('formats multiple days', () => {
      expect(formatDaysOfWeek([1, 3, 5])).toBe('월, 수, 금')
    })

    it('sorts days correctly', () => {
      expect(formatDaysOfWeek([5, 1, 3])).toBe('월, 수, 금')
    })

    it('handles empty array', () => {
      expect(formatDaysOfWeek([])).toBe('')
    })

    it('handles all days', () => {
      const result = formatDaysOfWeek([0, 1, 2, 3, 4, 5, 6])
      expect(result).toBe('일, 월, 화, 수, 목, 금, 토')
    })
  })

  describe('formatTime', () => {
    it('returns time as is', () => {
      expect(formatTime('09:00')).toBe('09:00')
      expect(formatTime('14:30')).toBe('14:30')
      expect(formatTime('23:59')).toBe('23:59')
    })
  })
})
