# RAG 시스템 개발사양서

## 1. 프로젝트 개요

### 1.1 프로젝트 명
PDF 기반 RAG(Retrieval-Augmented Generation) 시스템

### 1.2 목적
PDF 문서를 벡터 데이터베이스에 저장하고, 사용자 질의에 대해 관련 정보를 검색하여 답변을 제공하는 채팅 시스템 구축

### 1.3 주요 기능
- PDF 문서 업로드 및 텍스트 추출
- 문서 임베딩 및 벡터 DB 저장
- 자연어 질의를 통한 문서 검색
- 채팅 인터페이스를 통한 대화형 정보 검색

---

## 2. 시스템 아키텍처

### 2.1 전체 구조
```
┌─────────────────┐
│   Frontend      │
│  (HTML/CSS/JS)  │
└────────┬────────┘
         │
         │ HTTP/WebSocket
         │
┌────────▼────────┐
│   Backend       │
│   (Python)      │
├─────────────────┤
│ - FastAPI/Flask │
│ - LangChain     │
│ - PDF Parser    │
└────────┬────────┘
         │
         │
┌────────▼────────┐
│   ChromaDB      │
│  (Vector DB)    │
│   Local Storage │
└─────────────────┘
```

### 2.2 기술 스택

#### Frontend
- **HTML5**: 웹 페이지 구조
- **CSS3**: 스타일링 및 레이아웃
- **JavaScript (ES6+)**: 클라이언트 로직 및 API 통신

#### Backend
- **Python 3.10+**: 백엔드 언어
- **FastAPI**: 웹 프레임워크
- **LangChain**: RAG 파이프라인 구축
- **PyPDF2 / pdfplumber**: PDF 파싱
- **sentence-transformers**: 텍스트 임베딩
- **Google Gemini API**: LLM 답변 생성

#### Vector Database
- **ChromaDB**: 로컬 벡터 데이터베이스

---

## 3. 세부 기능 명세

### 3.1 PDF 처리 모듈

#### 3.1.1 PDF 업로드
- **엔드포인트**: `POST /api/upload`
- **입력**: PDF 파일 (multipart/form-data)
- **처리**:
  1. 파일 유효성 검증 (확장자, 크기)
  2. 임시 저장소에 파일 저장
  3. PDF 텍스트 추출
- **출력**: 업로드 성공 여부 및 문서 ID

#### 3.1.2 텍스트 추출
- **라이브러리**: PyPDF2 또는 pdfplumber
- **기능**:
  - 페이지별 텍스트 추출
  - 특수문자 및 인코딩 처리
  - 텍스트 정제 (공백, 줄바꿈 정규화)

#### 3.1.3 텍스트 청킹(Chunking)
- **청크 크기**: 500-1000 토큰
- **오버랩**: 100-200 토큰
- **방법**: RecursiveCharacterTextSplitter 사용
- **메타데이터**: 페이지 번호, 문서명, 청크 인덱스

### 3.2 벡터 데이터베이스 모듈

#### 3.2.1 ChromaDB 설정
- **저장 경로**: `./chroma_db`
- **컬렉션명**: `pdf_documents`
- **영속성**: 로컬 디스크에 저장

#### 3.2.2 임베딩 생성
- **모델**:
  - `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (다국어 지원)
  - 또는 `jhgan/ko-sroberta-multitask` (한국어 특화)
- **차원**: 384 또는 768
- **배치 처리**: 청크 단위 임베딩 생성

#### 3.2.3 데이터 저장
- **엔드포인트**: `POST /api/index`
- **처리**:
  1. 텍스트 청크에 대한 임베딩 생성
  2. 메타데이터와 함께 ChromaDB에 저장
  3. 인덱싱 완료 상태 반환

### 3.3 검색(Retrieval) 모듈

#### 3.3.1 질의 처리
- **엔드포인트**: `POST /api/query`
- **입력**:
  ```json
  {
    "query": "사용자 질문",
    "top_k": 5
  }
  ```
- **처리**:
  1. 질의 텍스트 임베딩 생성
  2. ChromaDB에서 유사도 검색
  3. 상위 K개 문서 반환

#### 3.3.2 유사도 검색
- **알고리즘**: 코사인 유사도 (ChromaDB `hnsw:space=cosine`)
- **반환 개수**: 기본 10개 (설정 가능)
- **인접 페이지 포함**: 검색된 페이지의 앞뒤 페이지(±1) 자동 포함하여 문맥 완성도 향상
- **메타데이터 포함**: 페이지 번호, 유사도 점수, 원본 텍스트

#### 3.3.3 RAG 응답 생성
- **엔드포인트**: `POST /api/chat`
- **LLM**: Google Gemini API 사용
- **입력**:
  ```json
  {
    "message": "사용자 질문",
    "conversation_id": "선택적"
  }
  ```
- **처리**:
  1. 질의와 관련된 문서 검색
  2. 검색된 문서를 컨텍스트로 프롬프트 구성
  3. Gemini API를 통한 답변 생성
  4. 출처 정보와 함께 반환

### 3.4 채팅 UI 모듈

#### 3.4.1 레이아웃 구성
```
┌─────────────────────────────────┐
│         상단바                   │
│  [로고]    RAG 채팅 시스템       │
├─────────────────────────────────┤
│  사이드바    │   채팅 영역       │
│             │                    │
│ [파일 업로드]│  ┌──────────────┐│
│             │  │  AI: 답변1   ││
│ [업로드 목록]│  └──────────────┘│
│  - 문서1.pdf│  ┌──────────────┐│
│  - 문서2.pdf│  │  User: 질문  ││
│             │  └──────────────┘│
│             │                    │
│             │  ┌──────────────┐ │
│             │  │ [입력창]  [전송]│
│             │  └──────────────┘ │
└─────────────────────────────────┘
```

#### 3.4.2 주요 컴포넌트

**파일 업로드 영역**
- 드래그 앤 드롭 지원
- 파일 선택 버튼
- 업로드 진행률 표시
- 업로드된 파일 목록

**채팅 영역**
- 메시지 리스트 (스크롤 가능)
- 사용자/AI 메시지 구분 표시
- 출처 문서 링크
- 타임스탬프

**입력 영역**
- 텍스트 입력창
- 전송 버튼
- Enter 키 전송 지원

#### 3.4.3 UI/UX 요구사항
- 반응형 디자인 (모바일/태블릿/데스크톱)
- 로딩 인디케이터
- 에러 메시지 표시
- 부드러운 스크롤 애니메이션

---

## 4. API 명세

### 4.1 파일 업로드
```
POST /api/upload
Content-Type: multipart/form-data

Request:
- file: PDF 파일

Response:
{
  "success": true,
  "document_id": "doc_123456",
  "filename": "document.pdf",
  "pages": 10,
  "message": "파일이 성공적으로 업로드되었습니다."
}
```

### 4.2 문서 인덱싱
```
POST /api/index
Content-Type: application/json

Request:
{
  "document_id": "doc_123456"
}

Response:
{
  "success": true,
  "chunks_created": 45,
  "message": "문서 인덱싱이 완료되었습니다."
}
```

### 4.3 채팅 질의
```
POST /api/chat
Content-Type: application/json

Request:
{
  "message": "이 문서의 주요 내용은 무엇인가요?",
  "conversation_id": "conv_123"
}

Response:
{
  "success": true,
  "answer": "이 문서는 다음과 같은 주요 내용을 다룹니다...",
  "sources": [
    {
      "document": "document.pdf",
      "page": 3,
      "score": 0.92,
      "text": "관련 텍스트 일부..."
    }
  ],
  "conversation_id": "conv_123"
}
```

### 4.4 문서 목록 조회
```
GET /api/documents

Response:
{
  "success": true,
  "documents": [
    {
      "id": "doc_123456",
      "filename": "document1.pdf",
      "upload_date": "2025-11-13T10:30:00",
      "pages": 10,
      "chunks": 45
    }
  ]
}
```

### 4.5 문서 삭제
```
DELETE /api/documents/{document_id}

Response:
{
  "success": true,
  "message": "문서가 삭제되었습니다."
}
```

---

## 5. 디렉토리 구조

```
02_RAG/
├── backend/
│   ├── main.py                 # FastAPI 애플리케이션 진입점
│   ├── requirements.txt        # Python 의존성
│   ├── config.py              # 설정 파일
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic 모델
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_service.py     # PDF 처리 서비스
│   │   ├── vector_service.py  # 벡터 DB 서비스
│   │   └── rag_service.py     # RAG 로직
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # API 라우트
│   └── utils/
│       ├── __init__.py
│       └── helpers.py         # 유틸리티 함수
├── frontend/
│   ├── index.html             # 메인 HTML
│   ├── css/
│   │   └── style.css          # 스타일시트
│   ├── js/
│   │   ├── app.js             # 메인 JavaScript
│   │   ├── api.js             # API 통신
│   │   └── ui.js              # UI 컴포넌트
│   └── assets/
│       └── images/            # 이미지 리소스
├── chroma_db/                 # ChromaDB 저장소 (자동 생성)
├── uploads/                   # 업로드된 PDF 임시 저장
├── .env                       # 환경 변수
├── .gitignore
└── README.md
```

---

## 6. 데이터 모델

### 6.1 문서 메타데이터
```python
{
    "document_id": str,        # 문서 고유 ID
    "filename": str,           # 파일명
    "upload_date": datetime,   # 업로드 일시
    "total_pages": int,        # 총 페이지 수
    "total_chunks": int,       # 생성된 청크 수
    "file_size": int,          # 파일 크기 (bytes)
    "status": str              # "processing" | "indexed" | "error"
}
```

### 6.2 텍스트 청크
```python
{
    "chunk_id": str,           # 청크 고유 ID
    "document_id": str,        # 문서 ID
    "page_number": int,        # 페이지 번호
    "chunk_index": int,        # 청크 순서
    "text": str,               # 텍스트 내용
    "embedding": List[float],  # 벡터 임베딩
    "metadata": dict           # 추가 메타데이터
}
```

### 6.3 대화 이력
```python
{
    "conversation_id": str,    # 대화 세션 ID
    "messages": [
        {
            "role": str,       # "user" | "assistant"
            "content": str,    # 메시지 내용
            "timestamp": datetime,
            "sources": List[dict]  # 참조 문서 (assistant만)
        }
    ]
}
```

---

## 7. 구현 단계

### Phase 1: 기본 인프라 구축
1. 프로젝트 디렉토리 생성
2. Python 가상환경 설정
3. 필요한 라이브러리 설치
4. ChromaDB 초기화

### Phase 2: Backend 개발
1. FastAPI 애플리케이션 기본 구조
2. PDF 업로드 및 파싱 기능
3. 텍스트 청킹 및 임베딩 생성
4. ChromaDB 통합
5. RAG 파이프라인 구현
6. API 엔드포인트 구현

### Phase 3: Frontend 개발
1. HTML 기본 레이아웃
2. CSS 스타일링
3. 파일 업로드 UI
4. 채팅 인터페이스
5. API 통신 로직
6. 에러 핸들링 및 사용자 피드백

### Phase 4: 통합 및 테스트
1. Frontend-Backend 통합
2. 기능 테스트
3. 성능 최적화
4. 버그 수정

### Phase 5: 배포 준비
1. 문서화 완료
2. 환경 변수 설정
3. 실행 스크립트 작성

---

## 8. 기술적 고려사항

### 8.1 성능 최적화
- **청킹 전략**: 문서 특성에 맞는 최적 청크 크기 선정
- **배치 처리**: 대량 문서 처리 시 배치 임베딩
- **캐싱**: 자주 조회되는 쿼리 결과 캐싱
- **비동기 처리**: 파일 업로드 및 인덱싱 비동기 처리

### 8.2 보안
- **파일 검증**: 업로드 파일 타입 및 크기 제한
- **입력 검증**: SQL Injection, XSS 방지
- **CORS 설정**: 허용된 도메인만 접근 가능
- **Rate Limiting**: API 요청 제한

### 8.3 확장성
- **멀티테넌시**: 사용자별 문서 격리
- **모델 교체**: 임베딩 모델 변경 가능한 구조
- **스케일링**: 향후 분산 벡터 DB로 전환 가능

### 8.4 사용성
- **에러 메시지**: 명확하고 친절한 한글 메시지
- **로딩 상태**: 진행 상황 실시간 표시
- **반응형 디자인**: 다양한 디바이스 지원

---

## 9. 의존성 라이브러리

### 9.1 Python (requirements.txt)
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
chromadb==0.4.18
langchain==0.1.0
langchain-community==0.0.10
langchain-google-genai==1.0.0
google-generativeai==0.3.0
sentence-transformers==2.2.2
PyPDF2==3.0.1
pdfplumber==0.10.3
python-dotenv==1.0.0
aiofiles==23.2.1
```

### 9.2 Frontend
- 외부 라이브러리 없이 순수 HTML/CSS/JS 사용
- (선택적) Marked.js - 마크다운 렌더링
- (선택적) DOMPurify - XSS 방지

---

## 10. 환경 변수 (.env)

```env
# Google Gemini API 설정
GEMINI_API_KEY=AIzaSyAYN3ECjWgk5mbH7XCL_QjO6juhP7mkpis

# ChromaDB 설정
CHROMA_DB_PATH=./chroma_db
COLLECTION_NAME=pdf_documents

# 임베딩 모델
EMBEDDING_MODEL=jhgan/ko-sroberta-multitask

# 파일 업로드 설정
MAX_UPLOAD_SIZE=50MB
UPLOAD_DIR=./uploads

# 청킹 설정
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# 검색 설정
DEFAULT_TOP_K=10

# 서버 설정
HOST=0.0.0.0
PORT=8000
```

---

## 11. 실행 방법

### 11.1 초기 설정
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 의존성 설치
pip install -r backend/requirements.txt
```

### 11.2 서버 실행
```bash
# Backend 서버 시작
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend 서버 (간단한 HTTP 서버)
cd frontend
python -m http.server 3000
```

### 11.3 접속
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API 문서: http://localhost:8000/docs

---

## 12. 테스트 시나리오

### 12.1 기본 기능 테스트
1. PDF 파일 업로드
2. 문서 인덱싱 확인
3. 간단한 질의 테스트
4. 답변 및 출처 확인

### 12.2 예외 상황 테스트
1. 잘못된 파일 형식 업로드
2. 매우 큰 파일 업로드
3. 네트워크 오류 처리
4. 빈 질의 입력

### 12.3 성능 테스트
1. 대용량 PDF 처리 시간
2. 동시 다중 사용자 접속
3. 검색 응답 시간

---

## 13. 향후 개선 사항

### 13.1 기능 추가
- 다중 파일 동시 업로드
- 대화 이력 저장 및 불러오기
- 문서 내 키워드 하이라이팅
- 문서 요약 기능
- 북마크 및 즐겨찾기

### 13.2 기술 개선
- WebSocket을 통한 실시간 스트리밍 응답
- 분산 벡터 데이터베이스 (Weaviate, Pinecone)
- GPU 가속 임베딩
- 하이브리드 검색 (키워드 + 벡터)

### 13.3 UI/UX 개선
- 다크 모드
- 음성 입력
- 모바일 앱 버전
- 다국어 지원

---

## 14. 참고 자료

### 14.1 공식 문서
- FastAPI: https://fastapi.tiangolo.com/
- ChromaDB: https://docs.trychroma.com/
- LangChain: https://python.langchain.com/
- Google Gemini API: https://ai.google.dev/

### 14.2 관련 논문
- RAG (Retrieval-Augmented Generation)
- Dense Passage Retrieval
- Sentence-BERT

---

## 문서 버전
- **버전**: 1.2
- **작성일**: 2025-11-13
- **작성자**: Claude Code
- **최종 수정일**: 2025-11-15
- **변경 사항**:
  - v1.2 (2025-11-15): 코사인 유사도 적용, 인접 페이지 자동 포함 기능 추가, RAG 프롬프트 개선
  - v1.1 (2025-11-13): Google Gemini API 통합 추가
