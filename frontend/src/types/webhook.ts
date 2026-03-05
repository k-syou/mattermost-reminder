export interface Webhook {
  id: string
  userId: string
  alias: string
  url: string
  createdAt: string
  updatedAt: string
}

export interface WebhookCreate {
  alias: string
  url: string
}

export interface WebhookUpdate {
  alias?: string
  url?: string
}
