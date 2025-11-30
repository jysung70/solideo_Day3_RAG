from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routes import router
from config import settings
import os

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="RAG 시스템 API",
    description="PDF 기반 RAG(Retrieval-Augmented Generation) 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(router, prefix="/api", tags=["API"])

# 시작 이벤트
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    print("=" * 60)
    print("RAG 시스템 서버 시작")
    print("=" * 60)
    print(f"서버 주소: http://{settings.HOST}:{settings.PORT}")
    print(f"API 문서: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"ChromaDB 경로: {settings.CHROMA_DB_PATH}")
    print(f"업로드 디렉토리: {settings.UPLOAD_DIR}")
    print("=" * 60)

# 종료 이벤트
@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    print("RAG 시스템 서버 종료")

# 루트 엔드포인트
@app.get("/")
async def root():
    """루트 경로"""
    return {
        "message": "RAG 시스템 API 서버",
        "version": "1.0.0",
        "docs": "/docs",
        "api": "/api"
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
