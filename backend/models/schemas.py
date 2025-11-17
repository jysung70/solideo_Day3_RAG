from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# 응답 모델
class BaseResponse(BaseModel):
    """기본 응답 모델"""
    success: bool
    message: str

# 파일 업로드 관련
class UploadResponse(BaseResponse):
    """파일 업로드 응답"""
    document_id: Optional[str] = None
    filename: Optional[str] = None
    pages: Optional[int] = None

# 문서 인덱싱 관련
class IndexRequest(BaseModel):
    """문서 인덱싱 요청"""
    document_id: str

class IndexResponse(BaseResponse):
    """문서 인덱싱 응답"""
    chunks_created: Optional[int] = None

# 채팅 관련
class ChatRequest(BaseModel):
    """채팅 요청"""
    message: str = Field(..., min_length=1, description="사용자 질문")
    conversation_id: Optional[str] = None

class SourceDocument(BaseModel):
    """출처 문서 정보"""
    document: str
    page: int
    score: float
    text: str

class ChatResponse(BaseResponse):
    """채팅 응답"""
    answer: Optional[str] = None
    sources: Optional[List[SourceDocument]] = None
    conversation_id: Optional[str] = None

# 검색 관련
class QueryRequest(BaseModel):
    """검색 요청"""
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)

class QueryResponse(BaseResponse):
    """검색 응답"""
    results: Optional[List[SourceDocument]] = None

# 문서 관련
class DocumentInfo(BaseModel):
    """문서 정보"""
    id: str
    filename: str
    upload_date: str
    pages: int
    chunks: int

class DocumentListResponse(BaseResponse):
    """문서 목록 응답"""
    documents: Optional[List[DocumentInfo]] = None

class DeleteResponse(BaseResponse):
    """삭제 응답"""
    pass
