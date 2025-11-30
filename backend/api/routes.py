from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from models.schemas import (
    UploadResponse, IndexRequest, IndexResponse,
    ChatRequest, ChatResponse, QueryRequest, QueryResponse,
    DocumentListResponse, DeleteResponse, DocumentInfo, SourceDocument
)
from services.pdf_service import pdf_service
from services.vector_service import vector_service
from services.rag_service import rag_service

router = APIRouter()

# ============================================
# 파일 업로드 API
# ============================================

@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    PDF 파일 업로드
    """
    try:
        # 파일 읽기
        file_content = await file.read()
        file_size = len(file_content)

        # 파일 유효성 검사
        is_valid, error_message = pdf_service.validate_file(file.filename, file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)

        # 파일 저장
        document_id, file_path = pdf_service.save_uploaded_file(file_content, file.filename)

        # PDF 텍스트 추출 (페이지별)
        pages_data, num_pages = pdf_service.extract_text_from_pdf(file_path)

        return UploadResponse(
            success=True,
            message="파일이 성공적으로 업로드되었습니다.",
            document_id=document_id,
            filename=file.filename,
            pages=num_pages
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 업로드 중 오류 발생: {str(e)}")

# ============================================
# 문서 인덱싱 API
# ============================================

@router.post("/index", response_model=IndexResponse)
async def index_document(request: IndexRequest):
    """
    문서 인덱싱 (벡터 DB에 저장)
    """
    try:
        document_id = request.document_id

        # 파일 경로 찾기
        import os
        from config import settings

        file_path = None
        for filename in os.listdir(settings.UPLOAD_DIR):
            if filename.startswith(document_id):
                file_path = os.path.join(settings.UPLOAD_DIR, filename)
                original_filename = filename.replace(f"{document_id}_", "")
                break

        if not file_path:
            raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")

        # PDF 텍스트 추출 (페이지별)
        pages_data, num_pages = pdf_service.extract_text_from_pdf(file_path)

        # 텍스트 청킹 (페이지 정보 유지)
        chunks = pdf_service.create_chunks(pages_data, document_id, original_filename)

        # 벡터 DB에 저장
        vector_service.add_documents(chunks, document_id, original_filename, num_pages)

        return IndexResponse(
            success=True,
            message="문서 인덱싱이 완료되었습니다.",
            chunks_created=len(chunks)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 인덱싱 중 오류 발생: {str(e)}")

# ============================================
# 채팅 API
# ============================================

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    채팅 (RAG 기반 질의응답)
    """
    try:
        # RAG 서비스를 통한 답변 생성
        answer, sources, conversation_id = rag_service.generate_answer(
            query=request.message,
            conversation_id=request.conversation_id
        )

        # 출처 문서를 SourceDocument 모델로 변환
        source_documents = [
            SourceDocument(
                document=src["document"],
                page=src["page"],
                score=src["score"],
                text=src["text"]
            )
            for src in sources
        ]

        return ChatResponse(
            success=True,
            message="답변이 생성되었습니다.",
            answer=answer,
            sources=source_documents,
            conversation_id=conversation_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채팅 중 오류 발생: {str(e)}")

# ============================================
# 검색 API
# ============================================

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    문서 검색
    """
    try:
        # 벡터 검색
        results = vector_service.search(request.query, request.top_k)

        # 결과를 SourceDocument 모델로 변환
        source_documents = [
            SourceDocument(
                document=result["document"],
                page=result["page"],
                score=result["score"],
                text=result["text"]
            )
            for result in results
        ]

        return QueryResponse(
            success=True,
            message="검색이 완료되었습니다.",
            results=source_documents
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 중 오류 발생: {str(e)}")

# ============================================
# 문서 관리 API
# ============================================

@router.get("/documents", response_model=DocumentListResponse)
async def get_documents():
    """
    문서 목록 조회
    """
    try:
        documents = vector_service.get_all_documents()

        # DocumentInfo 모델로 변환
        document_list = [
            DocumentInfo(
                id=doc["id"],
                filename=doc["filename"],
                upload_date=doc["upload_date"],
                pages=doc["pages"],
                chunks=doc["chunks"]
            )
            for doc in documents
        ]

        return DocumentListResponse(
            success=True,
            message="문서 목록 조회가 완료되었습니다.",
            documents=document_list
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 목록 조회 중 오류 발생: {str(e)}")

@router.delete("/documents/{document_id}", response_model=DeleteResponse)
async def delete_document(document_id: str):
    """
    문서 삭제
    """
    try:
        # 벡터 DB에서 삭제
        vector_deleted = vector_service.delete_document(document_id)

        # 파일 시스템에서 삭제
        file_deleted = pdf_service.delete_file(document_id)

        if vector_deleted or file_deleted:
            return DeleteResponse(
                success=True,
                message="문서가 삭제되었습니다."
            )
        else:
            raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문서 삭제 중 오류 발생: {str(e)}")

# ============================================
# 디버깅 API
# ============================================

@router.get("/debug/pages/{page_number}")
async def debug_page_chunks(page_number: int):
    """
    특정 페이지의 모든 청크 조회 (디버깅용)
    """
    try:
        # ChromaDB에서 해당 페이지의 모든 청크 조회
        results = vector_service.collection.get(
            where={"page_number": page_number},
            include=["documents", "metadatas"]
        )

        chunks_info = []
        if results["ids"]:
            for idx in range(len(results["ids"])):
                chunks_info.append({
                    "chunk_id": results["ids"][idx],
                    "metadata": results["metadatas"][idx],
                    "text_preview": results["documents"][idx][:500],  # 처음 500자
                    "text_length": len(results["documents"][idx])
                })

        return {
            "success": True,
            "page_number": page_number,
            "chunks_found": len(chunks_info),
            "chunks": chunks_info
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"디버깅 중 오류: {str(e)}")

# ============================================
# 헬스 체크 API
# ============================================

@router.get("/health")
async def health_check():
    """
    서버 상태 확인
    """
    return {
        "status": "healthy",
        "message": "RAG 시스템이 정상 작동 중입니다."
    }
