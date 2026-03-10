export interface Message {
  id: string
  userId: string
  content: string
  daysOfWeek: number[]
  sendTime: string
  sendTimes?: string[]
  repeatCycle?: 'daily' | 'weekly'
  sendOnce?: boolean
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
  repeatCycle?: 'daily' | 'weekly'
  sendOnce?: boolean
  webhookUrl: string
  isActive?: boolean
}

export interface MessageUpdate {
  content?: string
  daysOfWeek?: number[]
  sendTime?: string
  sendTimes?: string[]
  repeatCycle?: 'daily' | 'weekly'
  sendOnce?: boolean
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
}
