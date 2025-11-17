"""청킹 프로세스 시뮬레이션 - 페이지 6 내용이 어느 청크에 있는지 확인"""
import PyPDF2

pdf_path = "backend/uploads/doc_73d98794a215_표준프레임워크_보안개발_가이드(2024.02).pdf"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

print("=" * 80)
print("PDF 청킹 시뮬레이션")
print("=" * 80)

# PDF 텍스트 추출 (전체)
with open(pdf_path, 'rb') as file:
    pdf_reader = PyPDF2.PdfReader(file)
    num_pages = len(pdf_reader.pages)

    print(f"\n총 페이지 수: {num_pages}")

    # 페이지별 텍스트 추출
    text_by_page = []
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text = page.extract_text()

        # 텍스트 정제 (pdf_service.py와 동일)
        text = " ".join(text.split())
        text_by_page.append(text)

    # 모든 페이지 텍스트 결합
    full_text = "\n\n".join(text_by_page)

    print(f"전체 텍스트 길이: {len(full_text)} 자")

# 청킹 (pdf_service.py와 동일한 로직)
print("\n" + "=" * 80)
print("텍스트 청킹")
print("=" * 80)

chunks = []
text_length = len(full_text)
start = 0
chunk_index = 0

while start < text_length:
    end = start + CHUNK_SIZE
    chunk = full_text[start:end]
    chunks.append({
        "chunk_index": chunk_index,
        "start": start,
        "end": min(end, text_length),
        "text": chunk
    })
    start += CHUNK_SIZE - CHUNK_OVERLAP
    chunk_index += 1

print(f"\n총 청크 수: {len(chunks)}")

# 페이지 6의 텍스트 찾기
print("\n" + "=" * 80)
print("페이지 6 (page_num=5) 텍스트가 포함된 청크 찾기")
print("=" * 80)

# 페이지 6 텍스트 시작 부분 (고유한 문자열)
page_6_marker = "SQL Injection"

# 페이지 6 텍스트가 포함된 청크 찾기
matching_chunks = []
for i, chunk in enumerate(chunks):
    if page_6_marker in chunk["text"]:
        matching_chunks.append(i)

print(f"\n'SQL Injection' 키워드가 포함된 청크: {len(matching_chunks)}개")

for chunk_idx in matching_chunks[:10]:
    chunk = chunks[chunk_idx]
    print(f"\n{'=' * 60}")
    print(f"청크 인덱스: {chunk_idx}")
    print(f"위치: {chunk['start']} ~ {chunk['end']}")
    print(f"길이: {len(chunk['text'])} 자")
    print(f"\n청크 내용 (처음 300자):")
    print(chunk['text'][:300])

    # 'SQL Injection'이 포함된 부분 추출
    text = chunk['text']
    sql_index = text.find("SQL Injection")
    if sql_index != -1:
        context_start = max(0, sql_index - 100)
        context_end = min(len(text), sql_index + 200)
        print(f"\n'SQL Injection' 주변 문맥:")
        print(text[context_start:context_end])

# 특정 청크를 파일로 저장
print("\n" + "=" * 80)
print("청크 저장")
print("=" * 80)

for chunk_idx in matching_chunks[:3]:
    filename = f"chunk_{chunk_idx}_text.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(chunks[chunk_idx]["text"])
    print(f"청크 {chunk_idx} 저장: {filename}")

print("\n" + "=" * 80)
