"""PDF 3페이지 텍스트 추출 테스트"""
import PyPDF2

pdf_path = "backend/uploads/doc_73d98794a215_표준프레임워크_보안개발_가이드(2024.02).pdf"

print("=" * 80)
print("PDF 3페이지 텍스트 추출")
print("=" * 80)

with open(pdf_path, 'rb') as file:
    pdf_reader = PyPDF2.PdfReader(file)
    total_pages = len(pdf_reader.pages)

    print(f"\n총 페이지 수: {total_pages}")

    # 3페이지 (인덱스 2) 텍스트 추출
    print("\n" + "=" * 80)
    print("3페이지 (page_num=2) 원본 텍스트")
    print("=" * 80)

    page_3 = pdf_reader.pages[2]
    text_page_3 = page_3.extract_text()

    print(f"\n추출된 텍스트 길이: {len(text_page_3)} 자")

    # 텍스트를 파일로 저장
    with open("page_3_text.txt", "w", encoding="utf-8") as f:
        f.write(text_page_3)
    print("\n전체 텍스트를 'page_3_text.txt' 파일로 저장했습니다.")

    # SQL Injection 키워드 검색
    print("\n" + "=" * 80)
    print("SQL Injection 키워드 확인")
    print("=" * 80)

    if "SQL Injection" in text_page_3 or "SQL" in text_page_3:
        print("\n✓ 3페이지에 'SQL' 키워드가 포함되어 있습니다!")

        # SQL이 포함된 부분 찾기
        lines = text_page_3.split('\n')
        for i, line in enumerate(lines):
            if 'SQL' in line:
                print(f"\n라인 {i}: {line}")
    else:
        print("\n✗ 3페이지에 'SQL' 키워드가 없습니다.")

    # 2페이지와 4페이지도 확인
    print("\n" + "=" * 80)
    print("2페이지와 4페이지 확인")
    print("=" * 80)

    for page_num in [1, 3]:  # 2페이지, 4페이지
        page = pdf_reader.pages[page_num]
        text = page.extract_text()

        print(f"\n페이지 {page_num + 1} ({page_num + 1}페이지):")
        print(f"  길이: {len(text)} 자")
        if 'SQL' in text:
            print(f"  ✓ 'SQL' 키워드 포함")
        else:
            print(f"  ✗ 'SQL' 키워드 없음")

        # 처음 300자
        print(f"\n  처음 300자:")
        print(f"  {text[:300]}")

print("\n" + "=" * 80)
