export interface Message {
  id: string
  userId: string
  content: string
  daysOfWeek: number[] // 0=일요일, 6=토요일
  sendTime: string // "HH:mm"
  webhookUrl: string
  isActive: boolean
  createdAt: string
  updatedAt: string
}

export interface MessageCreate {
  content: string
  daysOfWeek: number[]
  sendTime: string
  webhookUrl: string
  isActive?: boolean
}

export interface MessageUpdate {
  content?: string
  daysOfWeek?: number[]
  sendTime?: string
  webhookUrl?: string
  isActive?: boolean
}
