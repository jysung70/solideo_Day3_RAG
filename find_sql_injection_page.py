"""PDF에서 'SQL Injection' 키워드가 있는 페이지 찾기"""
import PyPDF2

pdf_path = "backend/uploads/doc_73d98794a215_표준프레임워크_보안개발_가이드(2024.02).pdf"

print("=" * 80)
print("'SQL Injection' 키워드 검색")
print("=" * 80)

with open(pdf_path, 'rb') as file:
    pdf_reader = PyPDF2.PdfReader(file)
    total_pages = len(pdf_reader.pages)

    print(f"\n총 페이지 수: {total_pages}")

    sql_injection_pages = []

    for page_num in range(total_pages):
        page = pdf_reader.pages[page_num]
        text = page.extract_text()

        if "SQL" in text and "Injection" in text:
            sql_injection_pages.append({
                "page_num": page_num,
                "page_display": page_num + 1,
                "text": text
            })

    print(f"\n'SQL Injection' 키워드가 포함된 페이지: {len(sql_injection_pages)}개")

    for i, page_info in enumerate(sql_injection_pages[:10]):
        print(f"\n{'=' * 60}")
        print(f"[{i+1}] PDF 페이지 번호: {page_info['page_display']} (page_num={page_info['page_num']})")
        print("=" * 60)

        # SQL Injection이 포함된 부분 찾기
        text = page_info['text']
        lines = text.split('\n')

        print(f"\n총 라인 수: {len(lines)}")
        print(f"전체 텍스트 길이: {len(text)} 자")

        # SQL Injection이 포함된 라인 찾기
        sql_lines = []
        for line_num, line in enumerate(lines):
            if "SQL" in line and "Injection" in line:
                sql_lines.append((line_num, line))

        if sql_lines:
            print(f"\n'SQL Injection' 포함 라인: {len(sql_lines)}개")
            for line_num, line in sql_lines[:5]:
                print(f"  라인 {line_num}: {line[:100]}")

        # 텍스트를 파일로 저장
        filename = f"page_{page_info['page_num']}_text.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"\n텍스트 저장: {filename}")

        # 처음 500자
        print(f"\n처음 500자:")
        print(text[:500])

print("\n" + "=" * 80)
print("검색 완료")
print("=" * 80)
