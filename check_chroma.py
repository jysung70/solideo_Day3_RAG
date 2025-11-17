"""ChromaDB 컬렉션 확인 스크립트"""
import chromadb
from chromadb.config import Settings as ChromaSettings

# ChromaDB 클라이언트 초기화
client = chromadb.PersistentClient(
    path="./chroma_db",
    settings=ChromaSettings(anonymized_telemetry=False)
)

print("=" * 80)
print("ChromaDB 컬렉션 확인")
print("=" * 80)

# 모든 컬렉션 리스트
collections = client.list_collections()

print(f"\n총 컬렉션 개수: {len(collections)}")

for i, collection in enumerate(collections, 1):
    print(f"\n[{i}] 컬렉션 이름: {collection.name}")
    print(f"    문서 개수: {collection.count()}")
    print(f"    메타데이터: {collection.metadata}")

# pdf_documents 컬렉션 상세 확인
try:
    pdf_collection = client.get_collection("pdf_documents")
    count = pdf_collection.count()

    print("\n" + "=" * 80)
    print(f"'pdf_documents' 컬렉션 상세 정보")
    print("=" * 80)
    print(f"문서 개수: {count}")

    if count > 0:
        # 처음 5개 문서 샘플
        sample = pdf_collection.get(limit=5, include=["documents", "metadatas"])
        print(f"\n샘플 문서 (처음 5개):")
        for i, doc_id in enumerate(sample["ids"], 1):
            print(f"\n[{i}] ID: {doc_id}")
            print(f"    메타데이터: {sample['metadatas'][i-1]}")
            print(f"    내용 (처음 150자): {sample['documents'][i-1][:150]}...")

except Exception as e:
    print(f"\n'pdf_documents' 컬렉션 조회 실패: {e}")

print("\n" + "=" * 80)
