# 백엔드 개발 지식 베이스

## 1. RESTful API 설계

### 기본 원칙
- **리소스 중심 설계**: URL은 동사가 아닌 명사로 표현
  - 좋은 예: `/users`, `/products`, `/orders`
  - 나쁜 예: `/getUsers`, `/createProduct`, `/deleteOrder`

- **HTTP 메서드 활용**
  - GET: 리소스 조회 (멱등성 O, 안전함)
  - POST: 리소스 생성 (멱등성 X)
  - PUT: 리소스 전체 수정 (멱등성 O)
  - PATCH: 리소스 부분 수정 (멱등성 O)
  - DELETE: 리소스 삭제 (멱등성 O)

### 엔드포인트 네이밍 논쟁

**계층 구조 방식**: `/user/:id/profile`
- 장점: 리소스 간 관계가 명확, 직관적
- 단점: URL이 길어질 수 있음, 깊은 계층 시 복잡

**평면 구조 방식**: `/users/:id` + `/profiles/:userId`
- 장점: 각 리소스가 독립적, 확장성 좋음
- 단점: 리소스 간 관계 파악이 어려움

**실무 권장**: 2단계까지는 계층 구조, 그 이상은 쿼리 파라미터 사용
- `/users/:id/orders` ✅
- `/users/:id/orders/:orderId/items` ❌ → `/orders/:orderId?userId=xxx` ✅

### 버전 관리
- **URL 버저닝**: `/v1/users`, `/v2/users` (가장 일반적)
- **헤더 버저닝**: `Accept: application/vnd.api.v1+json` (RESTful하지만 복잡)

### 상태 코드 사용
- **200 OK**: 성공
- **201 Created**: 리소스 생성 성공 (POST)
- **204 No Content**: 성공했지만 반환할 내용 없음 (DELETE)
- **400 Bad Request**: 잘못된 요청
- **401 Unauthorized**: 인증 필요
- **403 Forbidden**: 권한 없음
- **404 Not Found**: 리소스 없음
- **500 Internal Server Error**: 서버 오류

---

## 2. 데이터베이스 설계 및 최적화

### 인덱스 (Index)
**개념**: 데이터 검색 속도를 높이기 위한 자료구조 (책의 목차와 유사)

**언제 사용?**
- WHERE 절에 자주 사용되는 컬럼
- JOIN에 사용되는 외래키
- ORDER BY에 사용되는 컬럼

**주의사항**:
- 쓰기 성능 저하 (INSERT, UPDATE, DELETE 시 인덱스도 갱신)
- 과도한 인덱스는 오히려 성능 저하
- 선택도가 높은 컬럼에 사용 (예: 이메일 O, 성별 X)

### N+1 문제
**발생 상황**: ORM 사용 시, 연관된 데이터를 조회할 때
```javascript
// N+1 문제 발생 예시
const users = await User.findAll(); // 1번의 쿼리
for (const user of users) {
  const posts = await user.getPosts(); // N번의 쿼리
}
```

**해결 방법**:
1. **Eager Loading**: `User.findAll({ include: [Post] })`
2. **JOIN 사용**: 한 번의 쿼리로 모두 가져오기
3. **DataLoader** 패턴 (GraphQL에서 많이 사용)

### 트랜잭션 (Transaction)
**개념**: 여러 작업을 하나의 논리적 단위로 묶어 처리
- **ACID 원칙**: Atomicity(원자성), Consistency(일관성), Isolation(격리성), Durability(지속성)

**사용 예시**:
```javascript
// 계좌 이체 시 트랜잭션 필요
await db.transaction(async (t) => {
  await Account.decrement('balance', { by: 100, where: { id: 1 }, transaction: t });
  await Account.increment('balance', { by: 100, where: { id: 2 }, transaction: t });
});
```

### 쿼리 최적화
1. **SELECT *  피하기**: 필요한 컬럼만 조회
2. **WHERE 조건 최적화**: 인덱스를 활용할 수 있도록
3. **EXPLAIN 분석**: 쿼리 실행 계획 확인
4. **Pagination**: LIMIT, OFFSET 사용 (큰 데이터셋)

---

## 3. 인증 및 보안

### JWT (JSON Web Token)
**구조**: Header.Payload.Signature
- Header: 토큰 타입, 알고리즘
- Payload: 사용자 정보 (claims)
- Signature: 변조 방지

**장점**:
- Stateless (서버에 세션 저장 불필요)
- 확장성 좋음 (분산 시스템에 유리)

**단점**:
- 토큰 크기가 큼 (매 요청마다 전송)
- 만료 전까지 무효화 불가 (Blacklist 필요)

**실무 패턴**:
- Access Token (짧은 만료 시간: 15분)
- Refresh Token (긴 만료 시간: 7일)

### OAuth 2.0
**개념**: 제3자 인증 프로토콜 (구글, 페이스북 로그인)

**흐름**:
1. 사용자가 "구글로 로그인" 클릭
2. 구글 로그인 페이지로 리다이렉트
3. 사용자 로그인 후 Authorization Code 발급
4. 백엔드가 Code로 Access Token 교환
5. Access Token으로 사용자 정보 조회

### 보안 체크리스트
- [ ] SQL Injection 방지 (Prepared Statement 사용)
- [ ] XSS 방지 (입력 검증, 출력 이스케이프)
- [ ] CSRF 방지 (CSRF 토큰 사용)
- [ ] 비밀번호 해싱 (bcrypt, Argon2 사용)
- [ ] HTTPS 사용
- [ ] Rate Limiting (API 호출 제한)
- [ ] 민감 정보 로깅 금지

---

## 4. 캐싱 전략

### 캐싱 레벨
1. **브라우저 캐싱**: HTTP 헤더 (Cache-Control, ETag)
2. **CDN 캐싱**: 정적 파일 (이미지, CSS, JS)
3. **서버 캐싱**: Redis, Memcached
4. **데이터베이스 캐싱**: Query Cache

### Redis 활용
**용도**:
- 세션 저장
- API 응답 캐싱
- Rate Limiting 구현
- 실시간 랭킹 (Sorted Set)
- Pub/Sub 메시징

**캐싱 전략**:
1. **Cache-Aside** (가장 일반적)
   - 데이터 요청 → 캐시 확인 → 없으면 DB 조회 → 캐시에 저장

2. **Write-Through**
   - 데이터 쓰기 → DB와 캐시에 동시 저장

3. **Write-Behind**
   - 데이터 쓰기 → 캐시에만 저장 → 나중에 배치로 DB 저장

**만료 전략**:
- **TTL (Time To Live)**: 일정 시간 후 자동 삭제
- **LRU (Least Recently Used)**: 가장 오래 사용 안 된 데이터 삭제

---

## 5. 성능 최적화

### API 응답 속도 개선
**문제**: API 응답이 3초 이상 걸림

**진단 순서**:
1. **로그 확인**: 어느 부분에서 시간이 걸리는지
2. **DB 쿼리 분석**: Slow Query Log 확인
3. **네트워크 확인**: 외부 API 호출 여부

**해결 방법**:
1. **데이터베이스 최적화**
   - 인덱스 추가
   - 쿼리 최적화 (N+1 문제 해결)
   - Connection Pool 크기 조정

2. **캐싱 도입**
   - Redis로 자주 조회되는 데이터 캐싱
   - HTTP 캐싱 헤더 활용

3. **비동기 처리**
   - 무거운 작업은 백그라운드 작업으로 (Message Queue)
   - Node.js: Bull, BullMQ
   - Python: Celery

4. **페이지네이션**
   - 대량 데이터는 분할 조회
   - Cursor-based Pagination (더 효율적)

### 대용량 트래픽 처리
**수평적 확장 (Scale Out)**:
- 서버 여러 대로 부하 분산
- 로드 밸런서 (Nginx, AWS ALB)
- Stateless 아키텍처 (세션을 Redis에 저장)

**수직적 확장 (Scale Up)**:
- 서버 성능 업그레이드 (CPU, 메모리)
- 한계 있음, 비용 비효율적

**데이터베이스 샤딩**:
- 데이터를 여러 DB에 분산 저장
- User ID 기준으로 샤딩 (예: 1-1000번 → DB1, 1001-2000번 → DB2)

---

## 6. 협업 시나리오별 대응

### 시나리오 1: API 설계 의견 충돌
**상황**: 팀원이 `/users/profile/:id` 를 주장하고, 당신은 `/user/:id/profile` 선호

**대응 방법**:
1. **상대 의견 경청**: "그렇게 생각하신 이유가 뭔가요?"
2. **기준 제시**: "확장성 측면에서 보면...", "REST 원칙에 따르면..."
3. **레퍼런스 제시**: "GitHub API는 이렇게 설계했는데요"
4. **타협안 찾기**: "중요 리소스는 계층 구조, 나머지는 평면 구조로 하는 건 어떨까요?"

### 시나리오 2: 성능 문제 논의
**상황**: API가 느리다는 불만, 원인 파악 필요

**대응 방법**:
1. **데이터 수집**: "정확히 어떤 API가 느린가요? 평균 응답 시간은?"
2. **가설 수립**: "DB 쿼리가 문제일 수 있어요", "캐싱이 안 되어서 그럴 수도..."
3. **실험 제안**: "Slow Query Log를 먼저 확인해볼까요?"
4. **우선순위 결정**: "가장 자주 호출되는 API부터 최적화하는 게 효과적일 것 같아요"

### 시나리오 3: 코드 리뷰
**좋은 코드 리뷰**:
- ✅ "이 부분은 인덱스를 추가하면 성능이 개선될 것 같아요"
- ✅ "에러 핸들링이 빠진 것 같은데, try-catch를 추가하면 어떨까요?"
- ✅ "변수명을 더 명확하게 하면 가독성이 좋아질 것 같습니다"

**나쁜 코드 리뷰**:
- ❌ "이건 왜 이렇게 짰나요?" (공격적)
- ❌ "이거 틀렸어요" (대안 제시 없음)
- ❌ "원래 이렇게 하는 거 아닌데요" (권위적)

---

## 7. 면접 질문 및 답변 예시

### 초급 질문
**Q: RESTful API가 무엇인가요?**
A: HTTP 프로토콜을 활용하여 리소스 중심으로 설계된 API입니다. URL은 명사로 표현하고, HTTP 메서드(GET, POST, PUT, DELETE)로 행위를 표현합니다.

**Q: GET과 POST의 차이는?**
A: GET은 리소스 조회에 사용하고 멱등성이 있으며 안전합니다. POST는 리소스 생성에 사용하고 멱등성이 없습니다. GET은 URL에 데이터를 포함하지만, POST는 Body에 데이터를 담습니다.

### 중급 질문
**Q: 데이터베이스 인덱스를 설명하고, 단점도 말씀해주세요.**
A: 인덱스는 검색 속도를 높이기 위한 자료구조로, B-Tree가 주로 사용됩니다. 단점은 쓰기 성능이 저하되고(INSERT, UPDATE 시 인덱스도 갱신), 저장 공간이 추가로 필요하며, 과도한 인덱스는 오히려 성능을 저하시킬 수 있습니다.

**Q: N+1 문제가 무엇이고 어떻게 해결하나요?**
A: ORM 사용 시 연관 데이터를 조회할 때, 메인 쿼리 1번 + 각 행마다 추가 쿼리 N번이 발생하는 문제입니다. Eager Loading이나 JOIN을 사용하여 한 번의 쿼리로 모든 데이터를 가져오면 해결됩니다.

### 고급 질문
**Q: 대규모 트래픽을 처리하기 위한 아키텍처를 설계한다면?**
A:
1. **로드 밸런싱**: Nginx로 여러 서버에 부하 분산
2. **캐싱**: Redis로 자주 조회되는 데이터 캐싱, CDN으로 정적 파일 제공
3. **데이터베이스**: Read Replica로 읽기 분산, 필요 시 샤딩
4. **비동기 처리**: 무거운 작업은 Message Queue로 처리
5. **모니터링**: 실시간 모니터링으로 병목 지점 파악

**Q: 동시에 같은 데이터를 수정하려 할 때 어떻게 처리하나요?**
A:
1. **낙관적 락(Optimistic Lock)**: 버전 컬럼을 두고, 수정 시 버전이 같은지 확인. 충돌 시 재시도.
2. **비관적 락(Pessimistic Lock)**: 데이터를 읽을 때 락을 걸어 다른 트랜잭션의 접근 차단.
3. **분산 락**: Redis를 이용한 분산 환경에서의 락 (Redlock 알고리즘)

---

## 8. 실무 팁

### 에러 처리 패턴
```javascript
// 좋은 에러 처리
try {
  const user = await User.findById(userId);
  if (!user) {
    throw new NotFoundError('사용자를 찾을 수 없습니다');
  }
  return user;
} catch (error) {
  if (error instanceof NotFoundError) {
    return res.status(404).json({ message: error.message });
  }
  // 예상치 못한 에러는 500
  logger.error(error);
  return res.status(500).json({ message: '서버 오류' });
}
```

### API 응답 포맷 통일
```javascript
// 성공 응답
{
  "success": true,
  "data": { ... },
  "message": "조회 성공"
}

// 실패 응답
{
  "success": false,
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "사용자를 찾을 수 없습니다"
  }
}
```

### 로깅 전략
- **운영 환경**: ERROR, WARN만 기록
- **개발 환경**: DEBUG, INFO 포함
- **민감 정보 제외**: 비밀번호, 토큰, 개인정보
- **구조화된 로깅**: JSON 형식으로 로그 저장 (ELK 스택 활용)

---

## 9. 협업 체크리스트

### 코드 작성 시
- [ ] 명확한 변수명, 함수명 사용
- [ ] 주석은 "왜(Why)"를 설명 ("무엇(What)"은 코드로)
- [ ] 한 함수는 한 가지 일만
- [ ] 매직 넘버 대신 상수 사용

### 코드 리뷰 시
- [ ] 기능이 요구사항을 만족하는가?
- [ ] 에러 처리가 적절한가?
- [ ] 성능 이슈는 없는가?
- [ ] 보안 취약점은 없는가?
- [ ] 테스트 코드가 있는가?

### 회의 시
- [ ] 발언 전에 상대 의견 요약
- [ ] 주장에는 반드시 근거 제시
- [ ] "안 됩니다" 대신 "이런 방법은 어떨까요?"
- [ ] 팀 전체 이익 우선

---

## 10. 용어 정리

- **API**: Application Programming Interface
- **REST**: Representational State Transfer
- **CRUD**: Create, Read, Update, Delete
- **ORM**: Object-Relational Mapping
- **JWT**: JSON Web Token
- **CORS**: Cross-Origin Resource Sharing
- **CDN**: Content Delivery Network
- **TTL**: Time To Live
- **Rate Limiting**: API 호출 횟수 제한
- **Idempotent**: 멱등성 (같은 요청을 여러 번 해도 결과가 같음)
- **Stateless**: 상태를 저장하지 않음 (각 요청이 독립적)
- **Connection Pool**: DB 연결을 미리 생성해두고 재사용
- **Payload**: 전송되는 실제 데이터
- **Latency**: 지연 시간
- **Throughput**: 처리량 (단위 시간당 처리 건수)