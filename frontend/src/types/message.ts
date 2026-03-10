export interface Message {
  id: string
  userId: string
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
