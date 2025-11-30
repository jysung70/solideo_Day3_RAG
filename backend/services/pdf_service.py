import os
import uuid
from typing import List, Dict, Tuple
import PyPDF2
from config import settings

class PDFService:
    """PDF 파일 처리 서비스"""

    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP

    def save_uploaded_file(self, file_content: bytes, filename: str) -> Tuple[str, str]:
        """
        업로드된 파일을 저장

        Args:
            file_content: 파일 내용
            filename: 파일명

        Returns:
            (document_id, file_path) 튜플
        """
        # 고유 문서 ID 생성
        document_id = f"doc_{uuid.uuid4().hex[:12]}"

        # 파일 저장 경로
        file_path = os.path.join(settings.UPLOAD_DIR, f"{document_id}_{filename}")

        # 파일 저장
        with open(file_path, "wb") as f:
            f.write(file_content)

        return document_id, file_path

    def extract_text_from_pdf(self, file_path: str) -> Tuple[List[Dict], int]:
        """
        PDF 파일에서 페이지별 텍스트 추출

        Args:
            file_path: PDF 파일 경로

        Returns:
            (페이지별 텍스트 리스트, 페이지 수) 튜플
            각 항목: {"page_number": int, "text": str}
        """
        pages_data = []

        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)

                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()

                    # 텍스트 정제
                    text = self._clean_text(text)

                    # 페이지 번호와 함께 저장 (1부터 시작)
                    pages_data.append({
                        "page_number": page_num + 1,
                        "text": text
                    })

                return pages_data, num_pages

        except Exception as e:
            raise Exception(f"PDF 텍스트 추출 중 오류 발생: {str(e)}")

    def _clean_text(self, text: str) -> str:
        """
        텍스트 정제

        Args:
            text: 원본 텍스트

        Returns:
            정제된 텍스트
        """
        if not text:
            return ""

        # 연속된 공백 제거
        text = " ".join(text.split())

        # 줄바꿈 정규화
        text = text.replace("\r\n", "\n")

        return text.strip()

    def _split_text(self, text: str) -> List[str]:
        """간단한 텍스트 분할 함수"""
        chunks = []
        text_length = len(text)
        start = 0

        while start < text_length:
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap

        return chunks

    def create_chunks(self, pages_data: List[Dict], document_id: str, filename: str) -> List[Dict]:
        """
        페이지별 텍스트를 청크로 분할 (페이지 번호 유지)

        Args:
            pages_data: 페이지별 텍스트 리스트 [{"page_number": int, "text": str}, ...]
            document_id: 문서 ID
            filename: 파일명

        Returns:
            청크 리스트 (메타데이터 포함)
        """
        chunk_documents = []
        chunk_counter = 0

        # 각 페이지별로 청크 생성
        for page_data in pages_data:
            page_number = page_data["page_number"]
            page_text = page_data["text"]

            # 페이지 텍스트가 비어있으면 건너뛰기
            if not page_text.strip():
                continue

            # 페이지 텍스트를 청크로 분할
            page_chunks = self._split_text(page_text)

            # 각 청크에 페이지 번호 메타데이터 추가
            for chunk_idx, chunk_text in enumerate(page_chunks):
                chunk_doc = {
                    "chunk_id": f"{document_id}_chunk_{chunk_counter}",
                    "document_id": document_id,
                    "filename": filename,
                    "chunk_index": chunk_counter,
                    "text": chunk_text,
                    "metadata": {
                        "source": filename,
                        "page_number": page_number,  # 실제 PDF 페이지 번호
                        "chunk_index": chunk_counter,
                        "page_chunk_index": chunk_idx  # 해당 페이지 내 청크 번호
                    }
                }
                chunk_documents.append(chunk_doc)
                chunk_counter += 1

        return chunk_documents

    def validate_file(self, filename: str, file_size: int) -> Tuple[bool, str]:
        """
        파일 유효성 검사

        Args:
            filename: 파일명
            file_size: 파일 크기

        Returns:
            (유효성 여부, 에러 메시지) 튜플
        """
        # 확장자 검사
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            return False, f"허용되지 않는 파일 형식입니다. PDF 파일만 업로드 가능합니다."

        # 파일 크기 검사
        if file_size > settings.MAX_UPLOAD_SIZE:
            max_size_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
            return False, f"파일 크기가 너무 큽니다. 최대 {max_size_mb}MB까지 업로드 가능합니다."

        return True, ""

    def delete_file(self, document_id: str) -> bool:
        """
        문서 파일 삭제

        Args:
            document_id: 문서 ID

        Returns:
            삭제 성공 여부
        """
        try:
            # 업로드 디렉토리에서 해당 document_id로 시작하는 파일 찾기
            for filename in os.listdir(settings.UPLOAD_DIR):
                if filename.startswith(document_id):
                    file_path = os.path.join(settings.UPLOAD_DIR, filename)
                    os.remove(file_path)
                    return True
            return False
        except Exception as e:
            print(f"파일 삭제 중 오류: {str(e)}")
            return False

# 전역 서비스 인스턴스
pdf_service = PDFService()
