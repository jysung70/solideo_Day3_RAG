import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from config import settings
import json
import os

class VectorService:
    """ChromaDB 벡터 데이터베이스 서비스"""

    def __init__(self):
        # ChromaDB 클라이언트 초기화
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_PATH,
            settings=ChromaSettings(
                anonymized_telemetry=False
            )
        )

        # 임베딩 모델 로드
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)

        # 컬렉션 가져오기 또는 생성
        self.collection = self._get_or_create_collection()

        # 문서 메타데이터 저장소 (간단한 JSON 파일)
        self.metadata_file = os.path.join(settings.CHROMA_DB_PATH, "documents_metadata.json")
        self.documents_metadata = self._load_metadata()

    def _get_or_create_collection(self):
        """컬렉션 가져오기 또는 생성"""
        try:
            # 기존 컬렉션 확인
            collection = self.client.get_collection(name=settings.COLLECTION_NAME)

            # 컬렉션 메타데이터 확인
            metadata = collection.metadata

            # 코사인 유사도가 아니면 재생성
            if metadata.get("hnsw:space") != "cosine":
                print(f"기존 컬렉션이 코사인 유사도를 사용하지 않습니다. 재생성합니다.")
                print(f"현재 설정: {metadata}")
                self.client.delete_collection(name=settings.COLLECTION_NAME)
                collection = self.client.create_collection(
                    name=settings.COLLECTION_NAME,
                    metadata={"description": "PDF 문서 임베딩 컬렉션", "hnsw:space": "cosine"}
                )
                print(f"새 컬렉션 '{settings.COLLECTION_NAME}' 생성됨 (코사인 유사도)")
            else:
                print(f"기존 컬렉션 '{settings.COLLECTION_NAME}' 사용 (코사인 유사도)")

        except Exception:
            # 컬렉션이 없으면 새로 생성
            collection = self.client.create_collection(
                name=settings.COLLECTION_NAME,
                metadata={"description": "PDF 문서 임베딩 컬렉션", "hnsw:space": "cosine"}
            )
            print(f"새 컬렉션 '{settings.COLLECTION_NAME}' 생성됨 (코사인 유사도)")

        return collection

    def _load_metadata(self) -> Dict:
        """문서 메타데이터 로드"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_metadata(self):
        """문서 메타데이터 저장"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.documents_metadata, f, ensure_ascii=False, indent=2)

    def add_documents(self, chunks: List[Dict], document_id: str, filename: str, total_pages: int):
        """
        문서 청크를 벡터 DB에 추가

        Args:
            chunks: 청크 리스트
            document_id: 문서 ID
            filename: 파일명
            total_pages: 총 페이지 수
        """
        if not chunks:
            raise ValueError("청크가 비어있습니다.")

        print(f"\n=== 문서 인덱싱 시작 ===")
        print(f"문서 ID: {document_id}")
        print(f"파일명: {filename}")
        print(f"총 페이지: {total_pages}")
        print(f"청크 개수: {len(chunks)}")

        try:
            # 텍스트 추출
            texts = [chunk["text"] for chunk in chunks]
            print(f"[1/4] 텍스트 추출 완료: {len(texts)}개 청크")

            # 임베딩 생성
            print(f"[2/4] 임베딩 생성 중...")
            embeddings = self.embedding_model.encode(texts, convert_to_numpy=True).tolist()
            print(f"[2/4] 임베딩 생성 완료: {len(embeddings)}개 벡터")

            # ChromaDB에 추가할 데이터 준비
            ids = [chunk["chunk_id"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            print(f"[3/4] 데이터 준비 완료")

            # ChromaDB에 추가
            print(f"[4/4] ChromaDB에 저장 중...")
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )

            # 저장 확인
            count_after = self.collection.count()
            print(f"[4/4] ChromaDB 저장 완료!")
            print(f"      현재 ChromaDB 총 청크 수: {count_after}")

            # 문서 메타데이터 저장
            from datetime import datetime
            self.documents_metadata[document_id] = {
                "id": document_id,
                "filename": filename,
                "upload_date": datetime.now().isoformat(),
                "pages": total_pages,
                "chunks": len(chunks)
            }
            self._save_metadata()
            print(f"[완료] 메타데이터 저장 완료")
            print(f"=== 문서 인덱싱 성공 ===\n")

        except Exception as e:
            print(f"\n[ERROR] 문서 인덱싱 실패!")
            print(f"오류 내용: {str(e)}")
            print(f"오류 타입: {type(e).__name__}")
            import traceback
            print(f"상세 스택:\n{traceback.format_exc()}")
            print(f"=== 문서 인덱싱 실패 ===\n")
            raise

    def search(self, query: str, top_k: int = None, include_adjacent: bool = True) -> List[Dict]:
        """
        유사도 검색 (인접 페이지 포함 옵션)

        Args:
            query: 검색 쿼리
            top_k: 반환할 결과 개수
            include_adjacent: 검색된 페이지의 인접 페이지도 포함할지 여부

        Returns:
            검색 결과 리스트
        """
        if top_k is None:
            top_k = settings.DEFAULT_TOP_K

        print(f"\n=== 벡터 검색 시작 ===")
        print(f"쿼리: {query}")
        print(f"Top-K: {top_k}")
        print(f"인접 페이지 포함: {include_adjacent}")
        print(f"ChromaDB 총 청크 수: {self.collection.count()}")

        # 쿼리 임베딩 생성
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True).tolist()
        print(f"쿼리 임베딩 생성 완료")

        # ChromaDB에서 검색
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        # 결과 포맷팅
        search_results = []
        found_pages = set()  # 검색된 페이지 번호 추적

        if results["ids"] and len(results["ids"][0]) > 0:
            print(f"초기 검색 결과: {len(results['ids'][0])}개 발견")
            for idx in range(len(results["ids"][0])):
                # 코사인 거리를 유사도로 변환
                distance = results["distances"][0][idx]
                similarity_score = 1.0 - distance
                similarity_score = max(0.0, min(1.0, similarity_score))

                # 실제 PDF 페이지 번호 가져오기
                page_number = results["metadatas"][0][idx].get("page_number", 0)
                found_pages.add(page_number)

                full_text = results["documents"][0][idx]

                result = {
                    "document": results["metadatas"][0][idx].get("source", "Unknown"),
                    "page": page_number,
                    "score": round(similarity_score, 4),
                    "text": full_text,
                    "source_type": "direct"  # 직접 검색된 결과
                }
                search_results.append(result)

                # 로그 출력
                print(f"  [{idx+1}] 유사도: {similarity_score:.4f} ({similarity_score*100:.1f}%), 페이지: {page_number}, 텍스트 길이: {len(full_text)}자")

            # 인접 페이지 포함
            if include_adjacent:
                print(f"\n인접 페이지 검색 중...")
                adjacent_pages = set()
                for page_num in found_pages:
                    # 이전/다음 페이지 추가 (±1)
                    adjacent_pages.add(page_num - 1)
                    adjacent_pages.add(page_num + 1)

                # 이미 검색된 페이지는 제외
                adjacent_pages = adjacent_pages - found_pages

                # 인접 페이지의 청크 가져오기
                for adj_page in sorted(adjacent_pages):
                    if adj_page <= 0:  # 0 이하는 건너뛰기
                        continue

                    try:
                        adj_results = self.collection.get(
                            where={"page_number": adj_page},
                            include=["documents", "metadatas"]
                        )

                        if adj_results["ids"]:
                            print(f"  [인접] 페이지 {adj_page}: {len(adj_results['ids'])}개 청크 추가")
                            for idx in range(len(adj_results["ids"])):
                                result = {
                                    "document": adj_results["metadatas"][idx].get("source", "Unknown"),
                                    "page": adj_page,
                                    "score": 0.5,  # 인접 페이지는 중간 점수
                                    "text": adj_results["documents"][idx],
                                    "source_type": "adjacent"  # 인접 페이지로 추가된 결과
                                }
                                search_results.append(result)
                    except Exception as e:
                        print(f"  [경고] 페이지 {adj_page} 가져오기 실패: {e}")

                # 유사도 순으로 정렬하여 상위 결과만 유지
                # direct 검색 결과를 우선하되, 인접 페이지도 포함하여 균형있게 선택
                print(f"인접 페이지 포함 후 총 결과: {len(search_results)}개")

                # 최종 결과 수 제한 (기본 top_k 값 사용)
                max_results = top_k
                if len(search_results) > max_results:
                    # 유사도 순으로 정렬 (score 내림차순)
                    search_results.sort(key=lambda x: x["score"], reverse=True)
                    search_results = search_results[:max_results]
                    print(f"최종 결과를 {max_results}개로 제한")

                # 최종적으로 페이지 순서대로 정렬
                search_results.sort(key=lambda x: (x["page"], 0 if x["source_type"] == "direct" else 1))
                print(f"최종 반환 결과: {len(search_results)}개")

        else:
            print(f"검색 결과: 0개")

        print(f"=== 벡터 검색 완료 ===\n")
        return search_results

    def get_all_documents(self) -> List[Dict]:
        """
        모든 문서 메타데이터 조회

        Returns:
            문서 정보 리스트
        """
        documents = []
        for doc_id, metadata in self.documents_metadata.items():
            documents.append(metadata)

        # 업로드 날짜 기준 내림차순 정렬
        documents.sort(key=lambda x: x.get("upload_date", ""), reverse=True)
        return documents

    def delete_document(self, document_id: str) -> bool:
        """
        문서 삭제

        Args:
            document_id: 문서 ID

        Returns:
            삭제 성공 여부
        """
        try:
            # ChromaDB에서 해당 문서의 모든 청크 찾기
            results = self.collection.get(
                where={"source": self.documents_metadata[document_id]["filename"]}
            )

            if results["ids"]:
                # 청크 삭제
                self.collection.delete(ids=results["ids"])

            # 메타데이터에서 삭제
            if document_id in self.documents_metadata:
                del self.documents_metadata[document_id]
                self._save_metadata()

            return True

        except Exception as e:
            print(f"문서 삭제 중 오류: {str(e)}")
            return False

    def get_document_info(self, document_id: str) -> Optional[Dict]:
        """
        특정 문서 정보 조회

        Args:
            document_id: 문서 ID

        Returns:
            문서 정보 또는 None
        """
        return self.documents_metadata.get(document_id)

# 전역 서비스 인스턴스
vector_service = VectorService()
