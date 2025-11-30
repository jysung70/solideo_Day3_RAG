"""
RAG 시스템 디버깅 스크립트
- ChromaDB 내용 확인
- 검색 쿼리 테스트
"""
import sys
sys.path.append('backend')

from services.vector_service import vector_service
from sentence_transformers import SentenceTransformer
import chromadb

print("=" * 80)
print("RAG 시스템 디버깅")
print("=" * 80)

# 1. ChromaDB 컬렉션 정보 확인
print("\n[1단계] ChromaDB 컬렉션 정보")
print("-" * 80)
collection = vector_service.collection
count = collection.count()
print(f"총 청크 개수: {count}")

# 2. "SQL Injection" 키워드가 포함된 청크 찾기
print("\n[2단계] 'SQL Injection' 키워드 검색 (메타데이터)")
print("-" * 80)

# 모든 청크 가져오기
if count > 0:
    all_data = collection.get(
        limit=min(count, 500),  # 최대 500개만 조회
        include=["documents", "metadatas"]
    )

    sql_injection_chunks = []
    for i, doc in enumerate(all_data["documents"]):
        if "SQL" in doc or "sql" in doc or "Injection" in doc or "injection" in doc:
            sql_injection_chunks.append({
                "index": i,
                "id": all_data["ids"][i],
                "text": doc[:200],  # 처음 200자만
                "metadata": all_data["metadatas"][i]
            })

    print(f"'SQL' 또는 'Injection' 키워드 포함 청크: {len(sql_injection_chunks)}개")

    if sql_injection_chunks:
        print("\n첫 3개 청크 샘플:")
        for i, chunk in enumerate(sql_injection_chunks[:3]):
            print(f"\n--- 청크 #{i+1} ---")
            print(f"ID: {chunk['id']}")
            print(f"메타데이터: {chunk['metadata']}")
            print(f"내용 (처음 200자): {chunk['text']}...")

# 3. 벡터 검색 테스트
print("\n" + "=" * 80)
print("[3단계] 벡터 검색 테스트")
print("-" * 80)

queries = [
    "SQL Injection에 대한 보안 대책",
    "SQL 인젝션",
    "SQL Injection 방어",
    "입력 데이터 검증",
    "보안 개발 가이드"
]

for query in queries:
    print(f"\n쿼리: '{query}'")
    print("-" * 40)

    # 벡터 검색
    results = vector_service.search(query, top_k=5)

    if results:
        print(f"검색 결과: {len(results)}개")
        for i, result in enumerate(results[:3], 1):
            print(f"\n  [{i}] 유사도: {result['score']:.4f}")
            print(f"      문서: {result['document']}")
            print(f"      페이지: {result['page']}")
            print(f"      내용: {result['text'][:150]}...")
    else:
        print("  검색 결과 없음")

# 4. 임베딩 모델 테스트
print("\n" + "=" * 80)
print("[4단계] 임베딩 유사도 직접 계산")
print("-" * 80)

query = "SQL Injection 보안 대책"
print(f"쿼리: '{query}'")

# 쿼리 임베딩
query_embedding = vector_service.embedding_model.encode([query])[0]
print(f"쿼리 임베딩 차원: {len(query_embedding)}")

# SQL Injection 관련 청크와 직접 유사도 계산
if sql_injection_chunks:
    print(f"\nSQL Injection 관련 청크 {len(sql_injection_chunks)}개와 유사도 계산:")

    # 처음 3개만 테스트
    for chunk in sql_injection_chunks[:3]:
        chunk_id = chunk['id']

        # ChromaDB에서 해당 청크의 임베딩 가져오기
        chunk_data = collection.get(
            ids=[chunk_id],
            include=["embeddings", "documents"]
        )

        if chunk_data["embeddings"]:
            chunk_embedding = chunk_data["embeddings"][0]

            # 코사인 유사도 계산
            import numpy as np
            similarity = np.dot(query_embedding, chunk_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
            )

            print(f"\n  청크 ID: {chunk_id}")
            print(f"  유사도: {similarity:.4f}")
            print(f"  내용: {chunk_data['documents'][0][:150]}...")

print("\n" + "=" * 80)
print("디버깅 완료")
print("=" * 80)
