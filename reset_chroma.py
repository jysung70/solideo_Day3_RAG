"""ChromaDB 완전 초기화 스크립트"""
import chromadb
from chromadb.config import Settings as ChromaSettings
import os
import shutil

print("=" * 80)
print("ChromaDB 초기화")
print("=" * 80)

# 1. 기존 ChromaDB 삭제
chroma_path = "./chroma_db"
if os.path.exists(chroma_path):
    print(f"\n[1단계] 기존 ChromaDB 디렉토리 삭제 중...")
    try:
        shutil.rmtree(chroma_path)
        print("[OK] 삭제 완료")
    except Exception as e:
        print(f"[ERROR] 삭제 실패: {e}")

# 2. 새 ChromaDB 디렉토리 생성
print(f"\n[2단계] 새 ChromaDB 디렉토리 생성 중...")
os.makedirs(chroma_path, exist_ok=True)
print("[OK] 생성 완료")

# 3. 새 컬렉션 생성
print(f"\n[3단계] 새 컬렉션 생성 중...")
client = chromadb.PersistentClient(
    path=chroma_path,
    settings=ChromaSettings(anonymized_telemetry=False)
)

collection = client.create_collection(
    name="pdf_documents",
    metadata={"description": "PDF 문서 임베딩 컬렉션"}
)
print("[OK] 컬렉션 'pdf_documents' 생성 완료")

# 4. 확인
print(f"\n[4단계] 확인")
collections = client.list_collections()
print(f"컬렉션 개수: {len(collections)}")
for col in collections:
    print(f"  - {col.name}: {col.count()}개 문서")

print("\n" + "=" * 80)
print("초기화 완료!")
print("=" * 80)
