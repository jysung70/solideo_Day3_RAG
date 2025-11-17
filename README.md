# PDF 기반 RAG 시스템

PDF 문서를 벡터 데이터베이스에 저장하고, 사용자 질의에 대해 관련 정보를 검색하여 답변을 제공하는 채팅 시스템입니다.

## 주요 기능

- **PDF 문서 업로드**: 드래그 앤 드롭 또는 파일 선택을 통한 PDF 업로드
- **페이지별 텍스트 추출**: PDF 페이지 번호를 보존하여 정확한 출처 추적
- **문서 임베딩**: 한국어 특화 임베딩 모델을 사용한 벡터 변환
- **벡터 DB 저장**: ChromaDB를 사용한 로컬 벡터 데이터베이스 저장 (코사인 유사도)
- **스마트 검색**: 코사인 유사도 기반 검색 + **인접 페이지 자동 포함** (문맥 완성도 향상)
- **자연어 질의**: 업로드된 문서 기반 질의응답
- **출처 명시**: AI 답변에 정확한 페이지 번호 출처 표시
- **채팅 인터페이스**: 직관적인 대화형 UI

## 기술 스택

### Backend
- **Python 3.10+**
- **FastAPI**: 웹 프레임워크
- **ChromaDB**: 벡터 데이터베이스
- **Google Gemini API**: LLM 답변 생성
- **sentence-transformers**: 텍스트 임베딩 (jhgan/ko-sroberta-multitask)
- **PyPDF2**: PDF 파싱

### Frontend
- **HTML5**
- **CSS3**
- **JavaScript (ES6+)**

## 프로젝트 구조

```
02_RAG/
├── backend/              # FastAPI 백엔드
│   ├── main.py          # 애플리케이션 진입점
│   ├── config.py        # 설정 파일
│   ├── requirements.txt # Python 의존성
│   ├── api/
│   │   └── routes.py    # API 엔드포인트
│   ├── models/
│   │   └── schemas.py   # Pydantic 모델
│   └── services/
│       ├── pdf_service.py     # PDF 처리
│       ├── vector_service.py  # 벡터 DB 관리
│       └── rag_service.py     # RAG 파이프라인
│
├── frontend/            # 프론트엔드
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── app.js       # 메인 로직
│       ├── api.js       # API 통신
│       └── ui.js        # UI 컴포넌트
│
├── uploads/             # 업로드된 PDF 저장소
├── chroma_db/           # ChromaDB 데이터
├── venv/                # Python 가상 환경
├── .env                 # 환경 변수
└── README.md
```

## 설치 및 실행

### 1. 환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (Mac/Linux)
source venv/bin/activate

# 의존성 설치
pip install -r backend/requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일에서 Google Gemini API 키를 설정하세요:

```env
GEMINI_API_KEY=your_api_key_here
```

### 3. 서버 실행

**Backend 서버 시작:**
```bash
cd backend
python main.py
```

또는 uvicorn 직접 실행:
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend 서버 시작 (별도 터미널):**
```bash
cd frontend
python -m http.server 3000
```

### 4. 접속

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API 문서: http://localhost:8000/docs

## API 엔드포인트

### 파일 업로드
```
POST /api/upload
Content-Type: multipart/form-data
```

### 문서 인덱싱
```
POST /api/index
Content-Type: application/json
Body: { "document_id": "doc_xxx" }
```

### 채팅 (RAG)
```
POST /api/chat
Content-Type: application/json
Body: { "message": "질문", "conversation_id": "optional" }
```

### 문서 검색
```
POST /api/query
Content-Type: application/json
Body: { "query": "검색어", "top_k": 5 }
```

### 문서 목록 조회
```
GET /api/documents
```

### 문서 삭제
```
DELETE /api/documents/{document_id}
```

### 서버 상태 확인
```
GET /api/health
```

### 디버깅 API (개발용)
```
GET /api/debug/pages/{page_number}
```
특정 페이지의 모든 청크를 조회하여 데이터 검증

## 환경 변수 설명

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `GEMINI_API_KEY` | Google Gemini API 키 | - |
| `CHROMA_DB_PATH` | ChromaDB 저장 경로 | `./chroma_db` |
| `COLLECTION_NAME` | ChromaDB 컬렉션명 | `pdf_documents` |
| `EMBEDDING_MODEL` | 임베딩 모델 | `jhgan/ko-sroberta-multitask` |
| `MAX_UPLOAD_SIZE` | 최대 업로드 크기 | `50MB` |
| `UPLOAD_DIR` | 업로드 디렉토리 | `./uploads` |
| `CHUNK_SIZE` | 텍스트 청크 크기 | `1000` |
| `CHUNK_OVERLAP` | 청크 오버랩 | `200` |
| `DEFAULT_TOP_K` | 기본 검색 결과 수 | `10` |
| `HOST` | 서버 호스트 | `0.0.0.0` |
| `PORT` | 서버 포트 | `8000` |

## 사용 방법

1. **문서 업로드**
   - 사이드바의 파일 업로드 영역에 PDF 파일 드래그 또는 "파일 선택" 버튼 클릭
   - 업로드된 문서가 자동으로 인덱싱됨

2. **질의응답**
   - 채팅 입력창에 질문 입력
   - Enter 키 또는 "전송" 버튼 클릭
   - AI가 업로드된 문서를 기반으로 답변 제공

3. **출처 확인**
   - AI 답변 아래에 출처 문서 정보가 표시됨
   - 문서명, 페이지 번호, 유사도 점수 확인 가능

4. **문서 관리**
   - 사이드바에서 업로드된 문서 목록 확인
   - "삭제" 버튼으로 문서 제거

## 개발 정보

### 주요 라이브러리

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
chromadb==0.4.18
google-generativeai==0.3.0
sentence-transformers==2.2.2
PyPDF2==3.0.1
python-dotenv==1.0.0
```

### RAG 파이프라인

1. **PDF 업로드** → PDF 파일 저장
2. **텍스트 추출** → PyPDF2로 페이지별 텍스트 추출 (페이지 번호 보존)
3. **청킹** → 1000자 단위로 분할 (200자 오버랩, 페이지 메타데이터 유지)
4. **임베딩** → sentence-transformers로 벡터 변환
5. **저장** → ChromaDB에 임베딩 저장 (코사인 유사도 사용)
6. **검색** → 코사인 유사도 기반 Top-10 검색 + **인접 페이지 자동 포함**
7. **컨텍스트 구성** → 전체 텍스트를 LLM에 제공
8. **생성** → Gemini API로 구조화된 답변 생성 (출처 페이지 번호 명시)

## 보안 고려사항

- `.env` 파일은 절대 Git에 커밋하지 마세요
- API 키는 환경 변수로만 관리하세요
- 프로덕션 환경에서는 CORS 설정을 제한하세요
- 파일 업로드 크기 제한을 적절히 설정하세요

## 라이선스

This project is for educational purposes.

## 문의

문제가 발생하거나 개선 사항이 있으면 이슈를 등록해주세요.

---

**버전**: 1.2.0
**작성일**: 2025-11-15
**주요 개선사항 (v1.2.0)**:
- 코사인 유사도 적용으로 검색 정확도 향상
- 인접 페이지 자동 포함 기능으로 문맥 완성도 개선
- 개선된 RAG 프롬프트로 구조화된 답변 생성
- 페이지별 텍스트 추출 및 정확한 출처 추적
- 전체 텍스트 컨텍스트 제공으로 답변 품질 향상
