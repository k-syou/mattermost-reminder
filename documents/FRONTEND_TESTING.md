# 프론트엔드 테스트 가이드

이 문서는 Mattermost Reminder 프론트엔드 테스트 환경과 테스트 작성 방법을 설명합니다.

## 테스트 환경

- **테스트 프레임워크**: Vitest
- **Vue 테스트 유틸리티**: @vue/test-utils
- **DOM 환경**: happy-dom
- **상태 관리**: Pinia

## 설치된 패키지

```json
{
  "devDependencies": {
    "@vue/test-utils": "^2.4.6",
    "@vitest/ui": "^1.6.0",
    "happy-dom": "^15.11.6",
    "vitest": "^1.6.0"
  }
}
```

## 테스트 실행

### 모든 테스트 실행
```bash
npm run test
```

### 테스트 실행 (한 번만)
```bash
npm run test -- --run
```

### 테스트 UI 실행
```bash
npm run test:ui
```

### 커버리지 확인
```bash
npm run test:coverage
```

## 테스트 구조

```
frontend/src/test/
├── setup.ts                    # 테스트 전역 설정
├── components/                 # 컴포넌트 테스트
│   ├── DaySelector.test.ts
│   ├── TimeSelector.test.ts
│   └── WebhookSelector.test.ts
└── utils/                      # 유틸리티 테스트
    └── format.test.ts
```

## 작성된 테스트

### 1. DaySelector 컴포넌트 테스트

**테스트 항목:**
- ✅ 모든 요일 렌더링 (7개)
- ✅ 선택된 요일 표시
- ✅ 요일 토글 시 이벤트 발생
- ✅ 요일 미선택 시 에러 메시지 표시
- ✅ 요일 선택 시 에러 메시지 숨김
- ✅ modelValue prop 변경 시 업데이트

**테스트 파일:** `src/test/components/DaySelector.test.ts`

### 2. TimeSelector 컴포넌트 테스트

**테스트 항목:**
- ✅ 시간 입력 필드 렌더링
- ✅ 초기 시간 값 표시
- ✅ 시간 변경 시 이벤트 발생
- ✅ modelValue prop 변경 시 업데이트
- ✅ 타임존 정보 표시

**테스트 파일:** `src/test/components/TimeSelector.test.ts`

### 3. WebhookSelector 컴포넌트 테스트

**테스트 항목:**
- ✅ 웹훅 선택 드롭다운 렌더링
- ✅ Store에서 웹훅 목록 표시
- ✅ 선택된 웹훅 표시
- ✅ 웹훅 선택 시 이벤트 발생
- ✅ 웹훅 없을 때 에러 메시지 표시
- ✅ modelValue prop 변경 시 업데이트

**테스트 파일:** `src/test/components/WebhookSelector.test.ts`

### 4. Format 유틸리티 테스트

**테스트 항목:**
- ✅ formatDaysOfWeek: 단일 요일 포맷팅
- ✅ formatDaysOfWeek: 여러 요일 포맷팅
- ✅ formatDaysOfWeek: 요일 정렬
- ✅ formatDaysOfWeek: 빈 배열 처리
- ✅ formatDaysOfWeek: 모든 요일 처리
- ✅ formatTime: 시간 포맷팅

**테스트 파일:** `src/test/utils/format.test.ts`

## 테스트 작성 가이드

### 컴포넌트 테스트 예시

```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from '@/components/MyComponent.vue'

describe('MyComponent', () => {
  it('renders correctly', () => {
    const wrapper = mount(MyComponent, {
      props: {
        modelValue: 'test'
      }
    })
    
    expect(wrapper.text()).toContain('test')
  })
})
```

### Pinia Store 테스트 예시

```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useMyStore } from '@/stores/myStore'

describe('MyStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initializes correctly', () => {
    const store = useMyStore()
    expect(store.items).toEqual([])
  })
})
```

## 테스트 실행 결과

현재 테스트 상태:
- ✅ **23개 테스트 모두 통과**
- ✅ **4개 테스트 파일**
  - DaySelector: 6개 테스트
  - TimeSelector: 5개 테스트
  - WebhookSelector: 6개 테스트
  - Format utils: 6개 테스트

## 다음 단계

추가로 작성할 테스트:
- [ ] Pinia Store 테스트 (Auth, Webhook, Message)
- [ ] View 컴포넌트 테스트 (LoginView, HomeView, WebhookView, MessageView)
- [ ] Router Guard 테스트
- [ ] 통합 테스트 (E2E)

## 참고사항

### 테스트 설정

`vitest.config.ts`에서 다음 설정을 사용:
- `globals: true` - 전역 API 사용 가능
- `environment: 'happy-dom'` - DOM 환경
- `setupFiles` - 테스트 전 설정 파일

### Pinia 설정

`src/test/setup.ts`에서 각 테스트 전에 새로운 Pinia 인스턴스를 생성합니다.

### Router Stub

테스트에서 `router-link`와 `router-view`는 자동으로 stub됩니다.
