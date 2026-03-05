import { beforeEach, vi } from 'vitest'
import { config } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

// Mock Firebase before any imports
const mockAuth = {
  currentUser: null,
  onAuthStateChanged: vi.fn((_auth, callback) => {
    // Call callback immediately with null user
    callback(null)
    // Return unsubscribe function
    return vi.fn()
  }),
  signInWithEmailAndPassword: vi.fn(),
  createUserWithEmailAndPassword: vi.fn(),
  signOut: vi.fn()
}

const mockDb = {
  collection: vi.fn(),
  doc: vi.fn()
}

vi.mock('@/config/firebase', () => ({
  default: {},
  auth: mockAuth,
  db: mockDb
}))

// Mock firebase/auth functions
vi.mock('firebase/auth', () => ({
  getAuth: vi.fn(() => mockAuth),
  onAuthStateChanged: vi.fn((_auth, callback) => {
    callback(null)
    return vi.fn()
  }),
  signInWithEmailAndPassword: vi.fn(),
  createUserWithEmailAndPassword: vi.fn(),
  signOut: vi.fn(),
  type: {}
}))

// Mock firebase/app
vi.mock('firebase/app', () => ({
  initializeApp: vi.fn(() => ({})),
  getApps: vi.fn(() => [])
}))

// Mock firebase/firestore
vi.mock('firebase/firestore', () => ({
  getFirestore: vi.fn(() => mockDb),
  collection: vi.fn(),
  doc: vi.fn(),
  getDoc: vi.fn(),
  getDocs: vi.fn(),
  addDoc: vi.fn(),
  updateDoc: vi.fn(),
  deleteDoc: vi.fn(),
  query: vi.fn(),
  where: vi.fn(),
  orderBy: vi.fn()
}))

// Pinia 설정
beforeEach(() => {
  setActivePinia(createPinia())
})

// 전역 설정
config.global.stubs = {
  'router-link': true,
  'router-view': true
}
