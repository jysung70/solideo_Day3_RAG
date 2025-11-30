# RAG 시스템 사용 가이드

이 문서는 PDF 기반 RAG(Retrieval-Augmented Generation) 시스템의 설치 및 사용 방법을 설명합니다.

## 1. 시스템 개요

이 시스템은 사용자가 업로드한 PDF 문서를 분석하여, 관련된 질문에 대해 AI가 답변을 제공하는 서비스입니다.
- **주요 기능**: PDF 업로드, 문서 내용 검색, AI 기반 질의응답, 출처 페이지 표시
- **기술 스택**: Python (FastAPI), JavaScript, ChromaDB, Google Gemini API

## 2. 사전 요구 사항

- **Python 3.10 이상**이 설치되어 있어야 합니다.
- **Google Gemini API 키**가 필요합니다. (https://makersuite.google.com/app/apikey 에서 발급 가능)

## 3. 설치 방법

1. **프로젝트 폴더로 이동**
   ```bash
   cd c:/Users/JaeyoungSung/Documents/Solideo/Day3/02_RAG
   ```

2. **가상환경 생성 및 활성화**
   ```bash
   # 가상환경 생성
   python -m venv venv

   # 가상환경 활성화 (Windows)
   venv\Scripts\activate
   ```

3. **의존성 라이브러리 설치**
   ```bash
   pip install -r backend/requirements.txt
   ```

## 4. 환경 설정

1. 프로젝트 루트 디렉토리에 `.env` 파일을 생성하거나 엽니다.
2. 다음과 같이 API 키를 설정합니다.
   ```env
   GEMINI_API_KEY=여기에_발급받은_API_키를_입력하세요
   ```

## 5. 시스템 실행

시스템을 사용하려면 **백엔드(서버)**와 **프론트엔드(화면)**를 각각 실행해야 합니다. 두 개의 터미널(명령 프롬프트) 창을 열어주세요.

### 터미널 1: 백엔드 실행
```bash
# 가상환경 활성화 (이미 되어있다면 생략)
venv\Scripts\activate

# 백엔드 실행
python backend/main.py
```
* 정상 실행 시: `RAG 시스템 서버 시작` 메시지와 함께 `http://0.0.0.0:8000` 주소가 표시됩니다.

### 터미널 2: 프론트엔드 실행
```bash
# 가상환경 활성화 (이미 되어있다면 생략)
venv\Scripts\activate

# 프론트엔드 폴더로 이동
cd frontend

# 웹 서버 실행
python -m http.server 3000
```
* 정상 실행 시: `Serving HTTP on :: port 3000` 메시지가 표시됩니다.

## 6. 사용 방법

1. **웹 브라우저 접속**
   - 크롬(Chrome) 등의 브라우저를 열고 **[http://localhost:3000](http://localhost:3000)** 에 접속합니다.

2. **PDF 문서 업로드**
   - 화면 왼쪽의 "파일 선택" 버튼을 누르거나, 파일을 드래그하여 PDF 문서를 업로드합니다.
   - 업로드가 완료되면 문서 목록에 파일이 표시됩니다.

3. **질문하기**
   - 화면 중앙의 채팅 입력창에 문서 내용과 관련된 질문을 입력하고 엔터(Enter)를 칩니다.
   - 예: "이 문서의 주요 내용은 뭐야?", "보안 대책에 대해 알려줘"

4. **답변 확인**
   - AI가 생성한 답변과 함께, 참고한 문서의 **페이지 번호**가 표시됩니다.

## 7. 문제 해결

- **업로드 실패**: 파일이 PDF 형식이 맞는지, 크기가 너무 크지 않은지(50MB 제한) 확인하세요.
- **답변이 이상함**: 질문을 좀 더 구체적으로 하거나, 관련 내용이 포함된 문서를 업로드했는지 확인하세요.
- **서버 연결 오류**: 백엔드 서버(터미널 1)가 켜져 있는지 확인하세요.
