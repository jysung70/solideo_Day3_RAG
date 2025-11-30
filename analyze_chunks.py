"""ChromaDB 청크 분석 스크립트 - SQL Injection 관련 청크 찾기"""
import chromadb
from chromadb.config import Settings as ChromaSettings

print("=" * 80)
print("ChromaDB 청크 상세 분석")
print("=" * 80)

# ChromaDB 클라이언트 초기화
client = chromadb.PersistentClient(
    path="./backend/chroma_db",
    settings=ChromaSettings(anonymized_telemetry=False)
)

# 컬렉션 가져오기
try:
    collection = client.get_collection("pdf_documents")
    total_count = collection.count()

    print(f"\n총 청크 개수: {total_count}")

    if total_count == 0:
        print("\n[경고] ChromaDB가 비어있습니다!")
        print("백엔드 서버가 실행 중인 경우, 다른 프로세스가 데이터베이스를 사용 중일 수 있습니다.")
    else:
        print("\n" + "=" * 80)
        print("1단계: 모든 청크 조회")
        print("=" * 80)

        # 모든 청크 가져오기
        all_data = collection.get(
            limit=total_count,
            include=["documents", "metadatas"]
        )

        print(f"\n조회된 청크: {len(all_data['ids'])}개")

        # SQL Injection 키워드 검색
        print("\n" + "=" * 80)
        print("2단계: 'SQL Injection' 키워드 검색")
        print("=" * 80)

        sql_chunks = []
        for i, doc in enumerate(all_data["documents"]):
            doc_lower = doc.lower()
            if "sql" in doc_lower and ("injection" in doc_lower or "인젝션" in doc_lower):
                metadata = all_data["metadatas"][i]
                chunk_index = metadata.get("chunk_index", -1)

                sql_chunks.append({
                    "index": i,
                    "id": all_data["ids"][i],
                    "chunk_index": chunk_index,
                    "text": doc,
                    "metadata": metadata
                })

        print(f"\n'SQL Injection' 키워드 포함 청크: {len(sql_chunks)}개")

        if sql_chunks:
            print("\n상위 10개 청크:")
            for i, chunk in enumerate(sql_chunks[:10]):
                print(f"\n{'='*60}")
                print(f"[청크 #{i+1}]")
                print(f"ID: {chunk['id']}")
                print(f"청크 인덱스: {chunk['chunk_index']}")
                print(f"메타데이터: {chunk['metadata']}")
                print(f"\n내용 (처음 300자):")
                print(chunk['text'][:300])
                print("...")

        # 페이지별 청크 분포 확인
        print("\n" + "=" * 80)
        print("3단계: 페이지별 청크 분포")
        print("=" * 80)

        page_chunks = {}
        for i, metadata in enumerate(all_data["metadatas"]):
            chunk_index = metadata.get("chunk_index", -1)
            if chunk_index not in page_chunks:
                page_chunks[chunk_index] = []
            page_chunks[chunk_index].append(i)

        print(f"\n총 페이지(청크 인덱스): {len(page_chunks)}개")

        # 0~10 페이지의 청크 확인
        print("\n처음 10개 페이지의 청크:")
        for page_idx in sorted(page_chunks.keys())[:10]:
            chunk_count = len(page_chunks[page_idx])
            print(f"  청크 인덱스 {page_idx}: {chunk_count}개 청크")

            # 각 청크의 시작 부분 확인
            for chunk_i in page_chunks[page_idx]:
                text_preview = all_data["documents"][chunk_i][:100].replace('\n', ' ')
                print(f"    - {text_preview}...")

        # 3페이지(chunk_index=2 or 3) 상세 확인
        print("\n" + "=" * 80)
        print("4단계: 3페이지 청크 상세 확인 (chunk_index=2)")
        print("=" * 80)

        page_3_chunks = [
            i for i, m in enumerate(all_data["metadatas"])
            if m.get("chunk_index") == 2
        ]

        if page_3_chunks:
            print(f"\n3페이지(chunk_index=2) 청크 개수: {len(page_3_chunks)}개")
            for chunk_i in page_3_chunks:
                print(f"\n{'='*60}")
                print(f"ID: {all_data['ids'][chunk_i]}")
                print(f"메타데이터: {all_data['metadatas'][chunk_i]}")
                print(f"\n전체 내용:")
                print(all_data['documents'][chunk_i])
        else:
            print("\n3페이지(chunk_index=2) 청크를 찾을 수 없습니다.")

            # chunk_index=3도 확인
            page_3_alt_chunks = [
                i for i, m in enumerate(all_data["metadatas"])
                if m.get("chunk_index") == 3
            ]
            if page_3_alt_chunks:
                print(f"\nchunk_index=3 청크 개수: {len(page_3_alt_chunks)}개")
                for chunk_i in page_3_alt_chunks:
                    print(f"\n{'='*60}")
                    print(f"ID: {all_data['ids'][chunk_i]}")
                    print(f"메타데이터: {all_data['metadatas'][chunk_i]}")
                    print(f"\n전체 내용:")
                    print(all_data['documents'][chunk_i])

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("분석 완료")
print("=" * 80)
