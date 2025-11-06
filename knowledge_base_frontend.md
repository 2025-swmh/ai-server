# 프론트엔드 개발 지식 베이스

## 1. React 핵심 개념

### Component 설계 원칙
**단일 책임 원칙**: 하나의 컴포넌트는 하나의 역할만
```jsx
// ❌ 나쁜 예: 너무 많은 책임
function UserDashboard() {
  // 사용자 정보, 주문 내역, 통계, 설정 모두 처리
}

// ✅ 좋은 예: 책임 분리
function UserDashboard() {
  return (
    <>
      <UserProfile />
      <OrderHistory />
      <Statistics />
      <UserSettings />
    </>
  );
}
```

**Container-Presentational 패턴**:
- **Container**: 로직, 상태 관리, API 호출
- **Presentational**: UI 렌더링만, props로 데이터 받음

### State 관리
**useState vs useReducer**:
- `useState`: 간단한 상태 (2-3개 변수)
- `useReducer`: 복잡한 상태, 여러 하위 값, 다음 상태가 이전 상태에 의존

**전역 상태 관리 선택**:
- **Context API**: 소규모, 자주 변경되지 않는 상태 (테마, 인증)
- **Redux**: 대규모, 복잡한 상태, 미들웨어 필요
- **Zustand**: Redux보다 가벼움, 보일러플레이트 적음
- **Recoil/Jotai**: Atom 기반, React에 특화

### useEffect 사용법
**의존성 배열의 중요성**:
```jsx
// ❌ 무한 루프 위험
useEffect(() => {
  setCount(count + 1);
}); // 의존성 배열 없음

// ✅ 마운트 시에만 실행
useEffect(() => {
  fetchData();
}, []); // 빈 배열

// ✅ count 변경 시에만 실행
useEffect(() => {
  console.log(count);
}, [count]);
```

**Cleanup 함수**:
```jsx
useEffect(() => {
  const timer = setInterval(() => {
    console.log('tick');
  }, 1000);

  // Cleanup: 컴포넌트 언마운트 시 실행
  return () => clearInterval(timer);
}, []);
```

### 성능 최적화
**useMemo**: 계산 비용이 큰 값 메모이제이션
```jsx
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(a, b);
}, [a, b]);
```

**useCallback**: 함수 메모이제이션 (자식 컴포넌트에 props로 전달 시)
```jsx
const handleClick = useCallback(() => {
  doSomething(a, b);
}, [a, b]);
```

**React.memo**: 컴포넌트 메모이제이션 (props가 변경되지 않으면 리렌더링 방지)
```jsx
const MyComponent = React.memo(function MyComponent(props) {
  // ...
});
```

**Code Splitting (Lazy Loading)**:
```jsx
const LazyComponent = React.lazy(() => import('./LazyComponent'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LazyComponent />
    </Suspense>
  );
}
```

---

## 2. JavaScript/TypeScript

### ES6+ 주요 문법
**구조 분해 할당**:
```javascript
const { name, age } = user;
const [first, second, ...rest] = array;
```

**Spread/Rest 연산자**:
```javascript
const newArray = [...oldArray, newItem];
const newObject = { ...oldObject, updatedField: value };
```

**Optional Chaining**:
```javascript
const value = obj?.property?.nestedProperty;
// undefined 반환 (에러 없음)
```

**Nullish Coalescing**:
```javascript
const value = input ?? 'default'; // null/undefined만 처리
// vs
const value = input || 'default'; // falsy 값 모두 처리 (0, '', false 포함)
```

### 비동기 처리
**Promise vs Async/Await**:
```javascript
// Promise
fetch('/api/users')
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error(err));

// Async/Await (더 읽기 쉬움)
try {
  const res = await fetch('/api/users');
  const data = await res.json();
  console.log(data);
} catch (err) {
  console.error(err);
}
```

**병렬 처리**:
```javascript
// 순차 실행 (느림)
const user = await fetchUser();
const posts = await fetchPosts();

// 병렬 실행 (빠름)
const [user, posts] = await Promise.all([
  fetchUser(),
  fetchPosts()
]);
```

### TypeScript 핵심
**타입 vs 인터페이스**:
```typescript
// Type: Union, Intersection, 원시 타입 별칭
type ID = string | number;
type User = { name: string } & { age: number };

// Interface: 객체 형태, 확장 가능
interface User {
  name: string;
  age: number;
}
interface Admin extends User {
  role: string;
}
```

**제네릭 (Generic)**:
```typescript
function identity<T>(arg: T): T {
  return arg;
}

const result = identity<string>('hello'); // 타입 명시
const result2 = identity(123); // 타입 추론
```

**유틸리티 타입**:
```typescript
Partial<T>     // 모든 속성을 optional로
Required<T>    // 모든 속성을 required로
Pick<T, K>     // 특정 속성만 선택
Omit<T, K>     // 특정 속성 제외
Record<K, T>   // 키-값 쌍의 객체 타입
```

---

## 3. CSS 및 스타일링

### Flexbox vs Grid
**Flexbox**: 1차원 레이아웃 (행 또는 열)
```css
.container {
  display: flex;
  justify-content: center;   /* 주축 정렬 */
  align-items: center;        /* 교차축 정렬 */
  gap: 16px;                  /* 아이템 간 간격 */
}
```

**Grid**: 2차원 레이아웃 (행과 열)
```css
.container {
  display: grid;
  grid-template-columns: repeat(3, 1fr); /* 3개 컬럼 */
  gap: 16px;
}
```

### 반응형 디자인
**Mobile First 접근**:
```css
/* 기본: 모바일 */
.container {
  width: 100%;
}

/* 태블릿 */
@media (min-width: 768px) {
  .container {
    width: 750px;
  }
}

/* 데스크톱 */
@media (min-width: 1024px) {
  .container {
    width: 960px;
  }
}
```

### CSS-in-JS
**Styled-components**:
```jsx
const Button = styled.button`
  background: ${props => props.primary ? 'blue' : 'gray'};
  padding: 8px 16px;

  &:hover {
    opacity: 0.8;
  }
`;

<Button primary>Click me</Button>
```

**장점**: 컴포넌트 기반, 동적 스타일, 자동 벤더 프리픽스
**단점**: 런타임 오버헤드, 번들 크기 증가

### Tailwind CSS
```jsx
<button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
  Button
</button>
```

**장점**: 빠른 개발, 일관성, 번들 최적화 (PurgeCSS)
**단점**: 긴 클래스명, 학습 곡선

---

## 4. 성능 최적화

### 렌더링 최적화
**문제**: 불필요한 리렌더링
**해결**:
1. `React.memo`로 컴포넌트 메모이제이션
2. `useCallback`으로 함수 메모이제이션
3. `useMemo`로 값 메모이제이션
4. `key` prop 올바르게 사용 (index 사용 지양)

### 번들 크기 최적화
**Code Splitting**:
- Route 기반 분리 (React Router + Lazy)
- 무거운 라이브러리 동적 로드

**Tree Shaking**:
- ES6 모듈 사용
- 사용하지 않는 코드 자동 제거

**이미지 최적화**:
- WebP 포맷 사용
- Lazy Loading (`loading="lazy"`)
- 적절한 사이즈로 리사이징
- CDN 활용

### Web Vitals
**LCP (Largest Contentful Paint)**: 2.5초 이하
- 큰 이미지/비디오 최적화
- 서버 응답 시간 개선
- CSS/JS 블로킹 제거

**FID (First Input Delay)**: 100ms 이하
- JavaScript 실행 시간 줄이기
- Code Splitting
- Web Worker 사용

**CLS (Cumulative Layout Shift)**: 0.1 이하
- 이미지에 width/height 명시
- 동적 콘텐츠는 미리 공간 확보
- 폰트 로딩 최적화

---

## 5. API 통신 및 상태 관리

### REST API 호출
**Fetch API**:
```javascript
async function fetchUsers() {
  try {
    const response = await fetch('/api/users', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}
```

**Axios** (더 편리):
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// 인터셉터로 토큰 자동 추가
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const users = await api.get('/users');
```

### React Query (TanStack Query)
**서버 상태 관리의 혁명**:
```jsx
import { useQuery, useMutation } from '@tanstack/react-query';

// 데이터 조회
function Users() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: fetchUsers
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return <ul>{data.map(user => <li>{user.name}</li>)}</ul>;
}

// 데이터 변경
function AddUser() {
  const mutation = useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    }
  });

  return (
    <button onClick={() => mutation.mutate({ name: 'John' })}>
      Add User
    </button>
  );
}
```

**장점**:
- 자동 캐싱
- 백그라운드 업데이트
- 로딩/에러 상태 자동 관리
- 중복 요청 제거

---

## 6. 테스팅

### Jest + React Testing Library
**컴포넌트 테스트**:
```jsx
import { render, screen, fireEvent } from '@testing-library/react';

test('버튼 클릭 시 카운트 증가', () => {
  render(<Counter />);

  const button = screen.getByRole('button', { name: /increment/i });
  const count = screen.getByText(/count: 0/i);

  fireEvent.click(button);

  expect(screen.getByText(/count: 1/i)).toBeInTheDocument();
});
```

**비동기 테스트**:
```jsx
test('사용자 데이터 로드', async () => {
  render(<UserList />);

  expect(screen.getByText(/loading/i)).toBeInTheDocument();

  const users = await screen.findByRole('list');
  expect(users).toBeInTheDocument();
});
```

### E2E 테스트 (Cypress)
```javascript
describe('Login Flow', () => {
  it('로그인 성공', () => {
    cy.visit('/login');
    cy.get('input[name=email]').type('user@example.com');
    cy.get('input[name=password]').type('password123');
    cy.get('button[type=submit]').click();

    cy.url().should('include', '/dashboard');
    cy.contains('Welcome').should('be.visible');
  });
});
```

---

## 7. 보안

### XSS (Cross-Site Scripting) 방지
**React는 기본적으로 XSS 방어**:
```jsx
// 안전: 자동 이스케이프
<div>{userInput}</div>

// 위험: dangerouslySetInnerHTML 사용 시 주의
<div dangerouslySetInnerHTML={{ __html: sanitizedHTML }} />
```

**DOMPurify로 HTML 정제**:
```javascript
import DOMPurify from 'dompurify';

const clean = DOMPurify.sanitize(dirtyHTML);
```

### 인증 토큰 저장
**localStorage vs sessionStorage vs Cookie**:

| 저장소 | XSS 취약성 | CSRF 취약성 | 용도 |
|--------|-----------|-------------|------|
| localStorage | 높음 | 낮음 | 비권장 (보안 이슈) |
| sessionStorage | 높음 | 낮음 | 임시 데이터 |
| Cookie (httpOnly) | 낮음 | 높음 | **추천** (httpOnly, Secure 플래그) |

**권장 방식**:
- Access Token: httpOnly Cookie
- CSRF 토큰: 별도 헤더로 전송

### HTTPS 사용
- 모든 API 요청은 HTTPS
- Mixed Content 경고 확인

---

## 8. 협업 시나리오

### 시나리오 1: 컴포넌트 구조 논의
**상황**: 팀원이 모든 로직을 한 컴포넌트에 넣자고 제안

**대응**:
1. "관심사 분리 원칙에 따르면, Container와 Presentational을 나누는 게 유지보수에 유리합니다"
2. "테스트 작성도 분리된 컴포넌트가 더 쉽습니다"
3. "나중에 다른 곳에서 재사용하기도 편하고요"

### 시나리오 2: 상태 관리 라이브러리 선택
**상황**: Redux vs Zustand 중 선택

**질문할 내용**:
- "프로젝트 규모가 어느 정도인가요?"
- "미들웨어(Redux Saga, Thunk)가 필요한가요?"
- "팀원들이 Redux에 익숙한가요?"

**제안**:
- "소규모면 Zustand가 보일러플레이트가 적어서 생산성이 높습니다"
- "대규모이고 복잡한 상태 관리가 필요하면 Redux가 검증된 선택입니다"

### 시나리오 3: 성능 문제
**상황**: 페이지가 느리다는 피드백

**진단 순서**:
1. React DevTools Profiler로 리렌더링 확인
2. Chrome DevTools Performance 탭으로 병목 지점 파악
3. Network 탭으로 API 응답 시간 확인
4. Lighthouse로 Web Vitals 측정

**해결 방안 제시**:
- "불필요한 리렌더링이 많네요. React.memo를 적용해볼까요?"
- "이미지가 너무 큽니다. WebP로 변환하고 Lazy Loading을 적용하면 어떨까요?"
- "번들 크기가 크네요. Code Splitting을 해봅시다"

---

## 9. 디자이너와 협업

### 디자인 시스템 용어
- **토큰 (Token)**: 색상, 폰트, 간격 등의 기본 단위
  - `color-primary: #007bff`
  - `spacing-md: 16px`

- **컴포넌트 (Component)**: 버튼, 입력 필드 등 재사용 가능한 UI 요소

- **패턴 (Pattern)**: 여러 컴포넌트의 조합 (로그인 폼, 카드 레이아웃 등)

### 디자인 핸드오프
**Figma에서 확인할 것**:
1. **간격 (Spacing)**: 8px 단위로 일관되게 사용되었는지
2. **색상**: 정의된 컬러 팔레트에서 벗어나지 않았는지
3. **폰트**: 폰트 크기, 굵기, 행간이 명시되어 있는지
4. **상태**: Hover, Active, Disabled 상태가 정의되어 있는지
5. **반응형**: 모바일/태블릿/데스크톱 버전이 있는지

**질문할 것**:
- "이 요소의 최대 너비는 어떻게 되나요?"
- "텍스트가 길어지면 어떻게 처리하나요? (말줄임, 줄바꿈)"
- "로딩 중일 때는 어떻게 표시하나요?"
- "에러 상태는 어떻게 디자인되어 있나요?"

### 피드백 주는 방법
**좋은 피드백**:
- ✅ "이 버튼 높이가 44px인데, 모바일에서 터치하기 좋은 48px로 조정하면 어떨까요?"
- ✅ "색상 대비가 4.5:1이 안 되는데, 웹 접근성을 위해 조금 더 진하게 하면 좋을 것 같습니다"

**나쁜 피드백**:
- ❌ "이거 이상한데요"
- ❌ "제가 보기엔 파란색이 더 나은 것 같은데요" (주관적)

---

## 10. 백엔드와 협업

### API 명세 확인
**확인할 항목**:
1. **엔드포인트**: `GET /api/users/:id`
2. **요청 파라미터**: Query, Path, Body
3. **응답 형식**:
   ```json
   {
     "success": true,
     "data": { "id": 1, "name": "John" },
     "message": "Success"
   }
   ```
4. **에러 코드**: 400, 401, 404, 500 등의 의미
5. **페이지네이션**: Offset vs Cursor
6. **정렬/필터링**: Query 파라미터 형식

### 요청사항 전달
**좋은 요청**:
- ✅ "User API에서 `createdAt` 필드도 반환해주시면 '가입일' 표시에 사용할 수 있을 것 같습니다"
- ✅ "에러 응답에 `errorCode` 필드를 추가해주시면, 프론트에서 각 에러별로 다른 메시지를 보여줄 수 있습니다"

**나쁜 요청**:
- ❌ "이거 안 되는데요" (뭐가 문제인지 불명확)
- ❌ "이거 바꿔주세요" (왜 바꿔야 하는지 이유 없음)

### CORS 이슈 대응
**문제**: `Access-Control-Allow-Origin` 에러

**백엔드에 요청**:
- "CORS 정책 설정이 필요합니다"
- "개발 환경에서는 `http://localhost:3000`을 허용해주세요"
- "운영 환경에서는 실제 도메인을 허용해주세요"

**임시 해결** (개발 환경):
- Proxy 설정 (Create React App: `package.json`에 `"proxy": "http://localhost:8000"`)

---

## 11. 면접 질문 및 답변

### 초급 질문
**Q: React의 Virtual DOM이 무엇인가요?**
A: 실제 DOM의 가벼운 복사본입니다. React는 상태 변경 시 Virtual DOM에서 먼저 변경 사항을 계산하고, 실제 DOM과 비교(Diffing)하여 최소한의 변경만 실제 DOM에 적용합니다. 이를 통해 성능을 최적화합니다.

**Q: props와 state의 차이는?**
A: props는 부모 컴포넌트로부터 전달받는 읽기 전용 데이터이고, state는 컴포넌트 내부에서 관리하는 변경 가능한 데이터입니다. props는 컴포넌트 간 데이터 전달에, state는 컴포넌트 내부 상태 관리에 사용됩니다.

### 중급 질문
**Q: useEffect의 의존성 배열이 왜 중요한가요?**
A: 의존성 배열은 useEffect가 언제 실행될지 결정합니다. 빈 배열이면 마운트 시에만, 값이 있으면 해당 값 변경 시, 배열이 없으면 매 렌더링마다 실행됩니다. 잘못 설정하면 무한 루프나 예상치 못한 버그가 발생할 수 있습니다.

**Q: React의 리렌더링 조건은?**
A:
1. state가 변경될 때
2. props가 변경될 때
3. 부모 컴포넌트가 리렌더링될 때
4. Context 값이 변경될 때
5. forceUpdate() 호출 시 (비권장)

### 고급 질문
**Q: React 성능 최적화 기법을 설명해주세요**
A:
1. **React.memo**: props가 동일하면 리렌더링 방지
2. **useCallback/useMemo**: 함수/값 메모이제이션
3. **Code Splitting**: React.lazy와 Suspense로 필요한 코드만 로드
4. **Virtualization**: react-window로 긴 리스트 최적화
5. **Debounce/Throttle**: 과도한 이벤트 호출 제한
6. **Web Worker**: 무거운 연산을 별도 스레드에서 처리

**Q: CSR vs SSR vs SSG의 차이는?**
A:
- **CSR (Client-Side Rendering)**: 브라우저에서 JavaScript로 렌더링. SEO 불리, 초기 로딩 느림, 이후 빠름.
- **SSR (Server-Side Rendering)**: 서버에서 HTML 생성. SEO 유리, 초기 로딩 빠름, 서버 부하.
- **SSG (Static Site Generation)**: 빌드 시 HTML 생성. SEO 최고, 속도 빠름, 동적 콘텐츠 제한.

Next.js는 이 세 가지를 페이지별로 선택할 수 있습니다.

---

## 12. 최신 트렌드 (2024)

### React Server Components
- 서버에서만 실행되는 컴포넌트
- 번들 크기 감소, 서버 리소스 직접 접근
- Next.js 13+ App Router에서 기본

### 상태 관리 트렌드
- **Zustand**: Redux 대체, 간단한 API
- **Jotai**: Atomic 상태 관리
- **TanStack Query**: 서버 상태 관리의 표준

### 빌드 도구
- **Vite**: Webpack보다 빠른 개발 서버
- **Turbopack**: Next.js의 새로운 번들러 (Rust 기반)

---

## 13. 실무 팁

### 컴포넌트 네이밍
- **PascalCase**: 컴포넌트 파일/함수
  - `UserProfile.tsx`, `function UserProfile()`
- **camelCase**: 일반 함수, 변수
  - `fetchUsers()`, `userName`
- **접두사 활용**:
  - `use-`: 커스텀 훅 (`useAuth`, `useFetch`)
  - `handle-`: 이벤트 핸들러 (`handleClick`, `handleSubmit`)
  - `is-/has-`: 불리언 변수 (`isLoading`, `hasError`)

### 폴더 구조
```
src/
  ├── components/       # 공통 컴포넌트
  │   ├── Button/
  │   │   ├── Button.tsx
  │   │   ├── Button.test.tsx
  │   │   └── Button.styles.ts
  │   └── Input/
  ├── pages/            # 페이지 컴포넌트
  │   ├── Home/
  │   └── User/
  ├── hooks/            # 커스텀 훅
  ├── utils/            # 유틸 함수
  ├── api/              # API 호출 함수
  ├── types/            # TypeScript 타입 정의
  └── constants/        # 상수
```

### 에러 처리
```jsx
function UserProfile() {
  const { data, error, isLoading } = useQuery('user', fetchUser);

  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage message={error.message} />;
  if (!data) return <NotFound />;

  return <div>{data.name}</div>;
}
```

### 접근성 (a11y)
```jsx
// 시맨틱 HTML 사용
<button onClick={handleClick}>Click</button>  // ✅
<div onClick={handleClick}>Click</div>        // ❌

// aria 속성 활용
<button aria-label="닫기" onClick={handleClose}>
  <XIcon />
</button>

// 키보드 네비게이션
<div
  tabIndex={0}
  onKeyPress={(e) => e.key === 'Enter' && handleClick()}
>
  Click me
</div>
```

---

## 14. 용어 정리

- **CSR**: Client-Side Rendering
- **SSR**: Server-Side Rendering
- **SSG**: Static Site Generation
- **SPA**: Single Page Application
- **PWA**: Progressive Web App
- **SEO**: Search Engine Optimization
- **Hydration**: SSR에서 서버 HTML에 이벤트 연결
- **Tree Shaking**: 사용하지 않는 코드 제거
- **Code Splitting**: 코드를 여러 번들로 분리
- **Lazy Loading**: 필요할 때만 로드
- **Memoization**: 계산 결과를 캐싱
- **Reconciliation**: Virtual DOM 비교 과정
- **HOC**: Higher-Order Component (컴포넌트를 인자로 받아 새 컴포넌트 반환)
- **Render Props**: 렌더링 로직을 props로 전달
- **Compound Components**: 여러 컴포넌트가 함께 작동 (예: `<Select>` + `<Option>`)
- **Controlled Component**: React state로 제어되는 입력 요소
- **Uncontrolled Component**: DOM이 제어하는 입력 요소 (ref 사용)