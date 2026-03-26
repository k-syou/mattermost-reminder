/** API 목록/조회 응답과 동일. 간격 반복 시 timeRangeStart, timeRangeEnd, intervalSeconds 포함 */
export interface Message {
  id: string
  userId: string
  content: string
  daysOfWeek: number[]
  sendTime: string
  /** 고정 시간 목록 (여러 개). 구간 반복 사용 시 빈 배열 */
  sendTimes?: string[]
  repeatCycle?: 'daily' | 'weekly' | 'weekdays' | 'weekend'
  sendOnce?: boolean
  /** 구간 반복: 시작 시간 HH:mm */
  timeRangeStart?: string
  /** 구간 반복: 종료 시간 HH:mm */
  timeRangeEnd?: string
  /** 구간 반복: 간격(초). 1~86400 */
  intervalSeconds?: number
  webhookUrl: string
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface MessageCreate {
  content: string
  daysOfWeek: number[]
  sendTime: string
  sendTimes?: string[]
  repeatCycle?: 'daily' | 'weekly' | 'weekdays' | 'weekend'
  sendOnce?: boolean
  timeRangeStart?: string
  timeRangeEnd?: string
  intervalSeconds?: number
  webhookUrl: string
  isActive?: boolean
}

export interface MessageUpdate {
  content?: string
  daysOfWeek?: number[]
  sendTime?: string
  sendTimes?: string[]
  repeatCycle?: 'daily' | 'weekly' | 'weekdays' | 'weekend'
  sendOnce?: boolean
  timeRangeStart?: string
  timeRangeEnd?: string
  intervalSeconds?: number
  webhookUrl?: string
  isActive?: boolean
}

export interface SendLog {
  id: string
  messageId: string
  status: 'success' | 'error'
  sentAt: string
  error?: string
  contentPreview?: string
}

export interface MessageAIGenerateResponse {
  content: string
  daysOfWeek?: number[]
  sendTime?: string
  timeRangeStart?: string
  timeRangeEnd?: string
  intervalSeconds?: number
}
