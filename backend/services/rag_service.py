import uuid
from typing import List, Dict, Tuple
import google.generativeai as genai
from config import settings
from services.vector_service import vector_service

class RAGService:
    """RAG (Retrieval-Augmented Generation) 서비스"""

    def __init__(self):
        # Gemini API 설정
        genai.configure(api_key=settings.GEMINI_API_KEY)

        # Gemini 모델 초기화
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

        # 대화 이력 저장소 (메모리)
        self.conversations = {}

    def generate_answer(
        self,
        query: str,
        conversation_id: str = None,
        top_k: int = None
    ) -> Tuple[str, List[Dict], str]:
        """
        질문에 대한 답변 생성 (RAG)

        Args:
            query: 사용자 질문
            conversation_id: 대화 세션 ID (선택적)
            top_k: 검색할 문서 개수

        Returns:
            (답변, 출처 문서 리스트, conversation_id) 튜플
        """
        # 대화 ID가 없으면 새로 생성
        if not conversation_id:
            conversation_id = f"conv_{uuid.uuid4().hex[:12]}"

        # 관련 문서 검색
        search_results = vector_service.search(query, top_k)

        # 검색 결과가 없는 경우
        if not search_results:
            answer = "죄송합니다. 업로드된 문서에서 관련 정보를 찾을 수 없습니다. 문서를 업로드하거나 다른 질문을 해주세요."
            return answer, [], conversation_id

        # 컨텍스트 구성
        context = self._build_context(search_results)

        # 프롬프트 생성
        prompt = self._create_prompt(query, context)

        # Gemini API를 통한 답변 생성
        try:
            response = self.model.generate_content(prompt)
            answer = response.text
        except Exception as e:
            answer = f"답변 생성 중 오류가 발생했습니다: {str(e)}"

        # 대화 이력 저장
        self._save_conversation(conversation_id, query, answer, search_results)

        return answer, search_results, conversation_id

    def _build_context(self, search_results: List[Dict]) -> str:
        """
        검색 결과로부터 컨텍스트 구성

        Args:
            search_results: 검색 결과 리스트

        Returns:
            컨텍스트 문자열
        """
        context_parts = []

        for result in search_results:
            # 페이지 번호를 직접 참조 형식으로 사용
            context_parts.append(
                f"[{result['document']}, 페이지 {result['page']}]\n"
                f"{result['text']}\n"
            )

        context = "\n".join(context_parts)
        return context

    def _create_prompt(self, query: str, context: str) -> str:
        """
        RAG 프롬프트 생성

        Args:
            query: 사용자 질문
            context: 검색된 문서 컨텍스트

        Returns:
            프롬프트 문자열
        """
        prompt = f"""당신은 전문적인 문서 기반 질의응답 시스템입니다. 아래 제공된 문서 내용을 바탕으로 사용자의 질문에 정확하고 상세하며 완전한 답변을 제공하세요.

[문서 내용]
{context}

[사용자 질문]
{query}

[답변 지침]
1. 제공된 문서 내용만을 기반으로 답변하세요.
2. 문서에 없는 내용은 추측하지 마세요.
3. 답변은 **구조화되고 완전하게** 작성하세요:
   - 질문이 "설명해줘"인 경우: 정의, 특징, 방법, 대책 등을 모두 포함
   - 질문이 "대책은?"인 경우: 구체적인 방법들을 모두 나열
   - 가능한 한 문서의 모든 관련 정보를 포함
4. 답변을 논리적으로 구조화하세요:
   - 개념/정의
   - 상세 설명
   - 구체적인 방법/대책 (있는 경우)
   - 예시 (있는 경우)
5. 각 주요 내용마다 반드시 출처를 "(페이지 N)" 형식으로 명시하세요.
   - 예: "SQL Injection은 악의적인 코드가 삽입되는 공격입니다 (페이지 6)."
6. 여러 페이지의 정보를 종합하여 답변하되, 출처는 모두 표시하세요.
7. 한국어로 답변하세요.
8. 답변은 충분히 상세하게 작성하되, 문서에 있는 내용만 포함하세요.

답변:"""

        return prompt

    def _save_conversation(
        self,
        conversation_id: str,
        query: str,
        answer: str,
        sources: List[Dict]
    ):
        """
        대화 이력 저장

        Args:
            conversation_id: 대화 세션 ID
            query: 사용자 질문
            answer: 시스템 답변
            sources: 출처 문서
        """
        from datetime import datetime

        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = {
                "conversation_id": conversation_id,
                "messages": []
            }

        # 사용자 메시지 추가
        self.conversations[conversation_id]["messages"].append({
            "role": "user",
            "content": query,
            "timestamp": datetime.now().isoformat()
        })

        # 어시스턴트 메시지 추가
        self.conversations[conversation_id]["messages"].append({
            "role": "assistant",
            "content": answer,
            "timestamp": datetime.now().isoformat(),
            "sources": sources
        })

    def get_conversation(self, conversation_id: str) -> Dict:
        """
        대화 이력 조회

        Args:
            conversation_id: 대화 세션 ID

        Returns:
            대화 이력
        """
        return self.conversations.get(conversation_id, {})

    def clear_conversation(self, conversation_id: str) -> bool:
        """
        대화 이력 삭제

        Args:
            conversation_id: 대화 세션 ID

        Returns:
            삭제 성공 여부
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False

# 전역 서비스 인스턴스
rag_service = RAGService()
