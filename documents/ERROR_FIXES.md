# 에러 수정 내역

## 에러 1: npm install 의존성 충돌 (date-fns / date-fns-tz)

### 발생 위치
- **파일**: `frontend/package.json`
- **에러 라인**: npm install 실행 시
- **에러 타입**: ERESOLVE (의존성 해결 실패)

### 에러 메시지
```
npm error ERESOLVE unable to resolve dependency tree
npm error While resolving: mattermost-reminder-frontend@1.0.0
npm error Found: date-fns@3.6.0
npm error Could not resolve dependency:
npm error peer date-fns@"2.x" from date-fns-tz@2.0.1
```

### 원인 분석
- `date-fns@3.2.0`이 설치되었지만
- `date-fns-tz@2.0.1`이 `date-fns@2.x`를 peer dependency로 요구하여 버전 충돌 발생
- `date-fns` 3.x 버전은 타임존 기능을 내장 지원하므로 `date-fns-tz`가 더 이상 필요하지 않음

### 해결 방법
`date-fns-tz` 패키지를 제거하고 `date-fns` 3.x의 내장 타임존 기능을 사용

### 수정 내용
**수정 전:**
```json
"dependencies": {
  "date-fns": "^3.2.0",
  "date-fns-tz": "^2.0.0"
}
```

**수정 후:**
```json
"dependencies": {
  "date-fns": "^3.2.0"
}
```

### 참고사항
- `date-fns` 3.x 버전부터는 `date-fns-tz` 없이도 타임존 기능을 사용할 수 있습니다
- 타임존 관련 함수는 `date-fns`에서 직접 import하여 사용:
  ```typescript
  import { formatInTimeZone, zonedTimeToUtc } from 'date-fns-tz'
  // 대신
  import { format, toZonedTime } from 'date-fns'
  ```

### 적용 날짜
2026-03-05

### 검증 결과
✅ `npm install` 성공적으로 완료
- 362개 패키지 설치 완료
- 의존성 충돌 해결 확인

### 추가 경고사항
- 일부 deprecated 패키지 경고 (inflight, glob, rimraf 등) - 향후 업데이트 필요
- 22개 취약점 발견 (16 moderate, 6 high) - `npm audit fix` 실행 권장

---

## 추가 참고사항

### date-fns 3.x 타임존 사용법
```typescript
import { format, toZonedTime } from 'date-fns'

// Asia/Seoul 타임존으로 변환
const seoulTime = toZonedTime(new Date(), 'Asia/Seoul')
const formatted = format(seoulTime, 'HH:mm')
```

### 다음 단계
1. `npm install` 재실행하여 의존성 설치 확인
2. 타임존 관련 코드가 있다면 `date-fns` 3.x API로 마이그레이션

---

## 에러 2: npm audit fix --force 후 Vite 버전 호환성 문제

### 발생 위치
- **파일**: `frontend/package.json`
- **에러 라인**: npm audit fix 실행 후
- **에러 타입**: ERESOLVE (peer dependency 충돌)

### 에러 메시지
```
npm error ERESOLVE could not resolve
npm error While resolving: @vitejs/plugin-vue@5.2.4
npm error Found: vite@7.3.1
npm error Could not resolve dependency:
npm error peer vite@"^5.0.0 || ^6.0.0" from @vitejs/plugin-vue@5.2.4
```

### 원인 분석
- `npm audit fix --force`가 vite를 7.3.1로 업그레이드
- `@vitejs/plugin-vue@5.2.4`는 vite `^5.0.0 || ^6.0.0`만 지원
- vite 7.x와 호환되지 않아 peer dependency 충돌 발생

### 해결 방법
vite를 6.x 버전으로 다운그레이드하고 `@vitejs/plugin-vue`를 최신 버전(5.2.4)으로 유지

### 수정 내용
**수정 전:**
```json
"vite": "^7.3.1",
"@vitejs/plugin-vue": "^5.0.3"
```

**수정 후:**
```json
"vite": "^6.0.0",
"@vitejs/plugin-vue": "^5.2.4"
```

### 추가 조치
- `node_modules` 및 `package-lock.json` 삭제 후 재설치
- 깨끗한 상태에서 의존성 재설정

### 검증 결과
✅ `npm install` 성공적으로 완료
- 366개 패키지 설치 완료
- peer dependency 충돌 해결 확인
- 10개 moderate 취약점 남아있음 (Firebase 관련, 업스트림 이슈)

### 참고사항
- `npm audit fix --force`는 breaking change를 포함할 수 있으므로 신중히 사용 필요
- vite 7.x는 아직 `@vitejs/plugin-vue`와 완전히 호환되지 않음
- 남은 취약점(undici)은 Firebase SDK의 의존성으로 인한 것으로, Firebase 업데이트 대기 필요

### 적용 날짜
2026-03-05

---

## 에러 3: Firebase Functions 배포 시 AttributeError (auth._apps)

### 발생 위치
- **파일**: `functions/main.py`
- **에러 라인**: 13번째 줄
- **에러 타입**: AttributeError

### 에러 메시지
```
AttributeError: module 'firebase_admin.auth' has no attribute '_apps'
File "C:\Users\SSAFY\Desktop\dev\mattermost_reminder\functions\main.py", line 13, in <module>
    if not auth._apps:
           ^^^^^^^^^^
Error: Functions codebase could not be analyzed successfully. It may have a syntax or runtime error
```

### 원인 분석
- `firebase_admin.auth` 모듈에는 `_apps` 속성이 존재하지 않음
- Firebase Admin SDK에서 앱 초기화 상태를 확인하는 잘못된 방법 사용
- `_apps`는 private 속성이며 `firebase_admin` 모듈 레벨에만 존재 (권장되지 않음)

### 해결 방법
`get_app()` 함수를 try-except로 감싸서 앱이 이미 초기화되었는지 확인

### 수정 내용
**수정 전:**
```python
# Initialize Firebase Admin
if not auth._apps:
    # Use Application Default Credentials in production
    # For local development, use service account key
    if os.path.exists('serviceAccountKey.json'):
        cred = credentials.Certificate('serviceAccountKey.json')
        initialize_app(cred)
    else:
        # Use default credentials (for Firebase Functions)
        initialize_app()
```

**수정 후:**
```python
# Initialize Firebase Admin
try:
    # Try to get existing app to check if already initialized
    from firebase_admin import get_app
    get_app()
except ValueError:
    # App doesn't exist, initialize it
    # Use Application Default Credentials in production
    # For local development, use service account key
    if os.path.exists('serviceAccountKey.json'):
        cred = credentials.Certificate('serviceAccountKey.json')
        initialize_app(cred)
    else:
        # Use default credentials (for Firebase Functions)
        initialize_app()
```

### 참고사항
- `get_app()`은 앱이 존재하지 않으면 `ValueError`를 발생시킴
- 이는 Firebase Admin SDK에서 권장되는 앱 초기화 확인 방법
- `scheduled_function.py`와 `http_function.py`에서는 이미 올바른 방법 사용 중

### 검증 결과
✅ 코드 수정 완료
- Firebase Functions 배포 전 코드 분석 단계 통과 예상
- 다른 파일들(`scheduled_function.py`, `http_function.py`)과 일관된 패턴 사용

### 적용 날짜
2026-03-05

---

## 에러 4: Firebase Functions 배포 시 ModuleNotFoundError (dependencies)

### 발생 위치
- **파일**: `functions/main.py`
- **에러 라인**: 46번째 줄 (routers import 시)
- **에러 타입**: ModuleNotFoundError

### 에러 메시지
```
ModuleNotFoundError: No module named 'dependencies'
File "C:\Users\SSAFY\Desktop\dev\mattermost_reminder\functions\main.py", line 46, in <module>
    from dependencies import get_current_user
Error: Functions codebase could not be analyzed successfully. It may have a syntax or runtime error
```

### 원인 분석
- `main.py`에서 `from dependencies import get_current_user`를 import하지만 실제로는 사용하지 않음
- Firebase Functions 배포 시 Python 경로가 `functions` 디렉토리로 설정되지 않아 모듈을 찾을 수 없음
- routers를 import할 때 간접적으로 dependencies가 import되지만, main.py에서 직접 import하면 경로 문제 발생

### 해결 방법
1. `main.py`에서 사용하지 않는 `get_current_user` import 제거
2. Python 경로를 명시적으로 설정하여 routers import 시 경로 문제 해결

### 수정 내용
**수정 전:**
```python
# Import routers
from dependencies import get_current_user  # 사용하지 않음
from routers import webhooks, messages
```

**수정 후:**
```python
# Import routers (dependencies are imported within routers)
# Ensure proper Python path for Firebase Functions
import sys
import os
functions_dir = os.path.dirname(os.path.abspath(__file__))
if functions_dir not in sys.path:
    sys.path.insert(0, functions_dir)

from routers import webhooks, messages
```

### 참고사항
- `get_current_user`는 `routers/webhooks.py`와 `routers/messages.py`에서 직접 import하여 사용
- `main.py`에서는 routers만 import하면 되므로 `dependencies`를 직접 import할 필요 없음
- Firebase Functions 배포 시 Python 경로를 명시적으로 설정하여 모듈 import 문제 해결

### 검증 결과
✅ 코드 수정 완료
- 사용하지 않는 import 제거
- Python 경로 명시적 설정으로 모듈 import 문제 해결

### 적용 날짜
2026-03-05

---

## 에러 5: Pytest 테스트 실패 - 모듈 import 오류

### 발생 위치
- **파일**: `functions/tests/*.py`
- **에러 타입**: ModuleNotFoundError, FastAPI dependency injection mock 실패

### 에러 메시지
```
ModuleNotFoundError: No module named 'dependencies'
ModuleNotFoundError: No module named 'main'
ModuleNotFoundError: No module named 'scheduler'
```

### 원인 분석
1. pytest 실행 시 Python 경로가 `functions` 디렉토리로 설정되지 않음
2. FastAPI의 async dependency (`get_current_user`)를 `@patch`로 mock할 수 없음
3. `ExpiredIdTokenError` 생성자 인자 문제

### 해결 방법

#### 1. Python 경로 설정
**`tests/conftest.py`에 경로 추가:**
```python
import sys
import os

# Add parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

**`pytest.ini` 설정:**
```ini
[pytest]
testpaths = tests
pythonpath = .
asyncio_mode = auto
```

#### 2. FastAPI dependency override 사용
`@patch` 대신 FastAPI의 `app.dependency_overrides` 사용:

```python
@pytest.fixture
def client(mock_user_dict):
    """Test client with dependency override"""
    from dependencies import get_current_user
    from main import app
    
    async def override_get_current_user():
        return mock_user_dict
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()
```

#### 3. Async 함수 테스트 수정
- `scheduler.py`의 `send_scheduled_messages`는 async 함수이므로 `@pytest.mark.asyncio` 추가
- `httpx.AsyncClient` mock 처리

#### 4. ExpiredIdTokenError 테스트 수정
```python
# ExpiredIdTokenError가 InvalidIdTokenError의 서브클래스일 수 있으므로
# 예외 처리 순서 확인 및 테스트 수정
```

### 검증 결과
✅ 모든 테스트 통과 (14 passed)
- 인증 테스트: 5개 통과
- Webhook 테스트: 3개 통과
- Message 테스트: 3개 통과
- Scheduler 테스트: 2개 통과
- 통합 테스트: 1개 통과

### 적용 날짜
2026-03-05

---

## 에러 6: 메시지 전송시간 여러 개 / 특정시간 반복 저장 안 됨

### 발생 위치
- **파일**: `functions/routers/messages.py`
- **영향**: 메시지 생성(create_message), 메시지 수정(update_message)
- **증상**: 전송시간을 여러 개 추가해도 저장되지 않음. 특정시간 반복 사용 설정해도 적용되지 않음.

### 원인 분석
1. **전송시간 여러 개**  
   - `create_message`에서 `send_times = message.sendTimes if message.sendTimes else [message.sendTime]` 사용.  
   - Python에서 빈 리스트 `[]`는 falsy이므로, 클라이언트가 특정시간 반복 모드로 `sendTimes: []`를 보내면 `[message.sendTime]`으로 덮어써서 한 개 시간만 저장됨.  
   - 여러 개 보낼 때는 동작하지만, 빈 배열/특정시간 반복 전환 시 sendTimes가 의도와 다르게 저장될 수 있음.
2. **특정시간 반복**  
   - 특정시간 반복 사용 시 클라이언트는 `timeRangeStart`, `timeRangeEnd`, `intervalSeconds`와 함께 `sendTimes: []` 전송.  
   - 위 로직으로 `sendTimes`가 한 개 시간으로 덮어써지고, 스케줄러가 시간대+간격이 아닌 단일 시간으로 동작할 수 있음.  
   - `update_message`에서는 시간대 모드와 고정 시간 모드가 서로 배타적으로 정리되지 않아, 이전 모드 필드가 문서에 남을 수 있음.

### 해결 방법
1. **create_message**  
   - `send_times` 결정 시 `message.sendTimes is not None`으로만 판단하여, 클라이언트가 보낸 빈 배열 `[]`를 그대로 저장.  
   - 특정시간 반복일 때(timeRangeStart/End/intervalSeconds 모두 있음) `message_data["sendTimes"] = []`로 명시.
2. **update_message**  
   - 특정시간 반복으로 업데이트할 때: range 세 필드 설정 후 `sendTimes = []` 설정.  
   - 고정 전송시간으로 업데이트할 때: `sendTimes` 설정 후 `timeRangeStart`, `timeRangeEnd`, `intervalSeconds`를 `None`으로 초기화.

### 수정 내용
- **create_message**: `send_times = message.sendTimes if message.sendTimes is not None else [message.sendTime]` 로 변경. time range 세 필드가 모두 있을 때 `message_data["sendTimes"] = []` 추가.
- **update_message**: `use_time_range`일 때 range 세 필드 + `sendTimes = []`. `message.sendTimes`가 있고 길이 > 0일 때 range 세 필드를 `None`으로 설정. 그 외는 기존처럼 각 필드만 반영.

### 검증 결과
- create 시 `sendTimes: ["09:00", "10:00"]` 전송 시 문서에 여러 전송시간 저장.
- create 시 특정시간 반복 전송 시 시간대·간격 저장, sendTimes는 [].
- update 시 모드 전환 시 반대 모드 필드 제거.

### 적용 날짜
2026-03-06

---

## 에러 7: 특정 시간 반복 저장/수정 시 설정이 풀림, DB에 한 개 시간만 저장됨

### 발생 위치
- **파일**: `functions/routers/messages.py` (create_message, update_message)
- **증상**: 특정 시간 반복 사용 후 설정해도 수정 모달에 들어가면 설정이 풀려 있음. Firestore에는 여러 전송시간이 아닌 한 개 시간만 저장됨.

### 원인 분석
1. **time range 저장 조건**  
   - timeRangeStart/timeRangeEnd/intervalSeconds를 `is not None`만으로 저장해, 빈 문자열(`""`)이나 `intervalSeconds: 0`도 저장됨.  
   - 조회 시 빈 문자열/0이 오면 프론트에서 `useTimeRangeMode`가 false로 계산되어 수정 시 폼이 풀려 보임.
2. **sendTimes와 time range 동시 저장**  
   - time range가 유효할 때도 `sendTimes`를 요청값 그대로 넣어, 특정 시간 반복 모드에서 `sendTimes: []`가 아닌 한 개 시간이 들어갈 여지가 있음.

### 해결 방법
1. **create_message**  
   - `has_valid_range`: timeRangeStart/End가 비어 있지 않은 문자열이고, intervalSeconds가 존재하며 >= 1일 때만 True.  
   - `has_valid_range`일 때만 message_data에 timeRangeStart, timeRangeEnd, intervalSeconds를 넣고, **sendTimes는 반드시 []**로 저장.  
   - 그 외에는 sendTimes만 요청대로 저장.
2. **update_message**  
   - 특정 시간 반복 적용 시 `message.timeRangeStart`/End가 strip 후 비어 있지 않고, `message.intervalSeconds >= 1`일 때만 range 필드와 `sendTimes = []` 반영.  
   - 고정 전송시간만 보낼 때는 기존처럼 timeRange* 필드를 None으로 정리.

### 수정 내용
- **create_message**: `has_valid_range` 도입 후, 유효할 때만 timeRangeStart/End/intervalSeconds 저장 및 sendTimes=[] 강제.  
- **update_message**: `use_time_range` 조건에 start/end non-empty, intervalSeconds >= 1 추가 후, range 저장 시 strip 적용 및 sendTimes=[] 설정.

### 검증 결과
- 특정 시간 반복으로 생성/수정 후 수정 모달 재진입 시 설정 유지.
- Firestore에 time range 사용 시 sendTimes는 [], timeRangeStart/End/intervalSeconds만 저장.

### 적용 날짜
2026-03-06

---
