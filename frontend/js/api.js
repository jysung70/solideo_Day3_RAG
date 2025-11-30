// API 통신 모듈

const API_BASE_URL = 'http://localhost:8000/api';

/**
 * API 클래스
 */
class API {
    /**
     * PDF 파일 업로드
     * @param {File} file - 업로드할 PDF 파일
     * @param {Function} onProgress - 진행률 콜백
     * @returns {Promise<Object>} 업로드 응답
     */
    static async uploadPDF(file, onProgress) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_BASE_URL}/upload`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || '파일 업로드 실패');
            }

            return await response.json();
        } catch (error) {
            console.error('Upload error:', error);
            throw error;
        }
    }

    /**
     * 문서 인덱싱
     * @param {string} documentId - 문서 ID
     * @returns {Promise<Object>} 인덱싱 응답
     */
    static async indexDocument(documentId) {
        try {
            const response = await fetch(`${API_BASE_URL}/index`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ document_id: documentId })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || '문서 인덱싱 실패');
            }

            return await response.json();
        } catch (error) {
            console.error('Index error:', error);
            throw error;
        }
    }

    /**
     * 채팅 메시지 전송
     * @param {string} message - 사용자 메시지
     * @param {string|null} conversationId - 대화 ID (선택적)
     * @returns {Promise<Object>} 채팅 응답
     */
    static async sendMessage(message, conversationId = null) {
        try {
            const requestBody = { message };
            if (conversationId) {
                requestBody.conversation_id = conversationId;
            }

            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || '메시지 전송 실패');
            }

            return await response.json();
        } catch (error) {
            console.error('Chat error:', error);
            throw error;
        }
    }

    /**
     * 문서 검색
     * @param {string} query - 검색 쿼리
     * @param {number} topK - 반환할 결과 개수
     * @returns {Promise<Object>} 검색 응답
     */
    static async searchDocuments(query, topK = 5) {
        try {
            const response = await fetch(`${API_BASE_URL}/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    top_k: topK
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || '검색 실패');
            }

            return await response.json();
        } catch (error) {
            console.error('Search error:', error);
            throw error;
        }
    }

    /**
     * 문서 목록 조회
     * @returns {Promise<Object>} 문서 목록 응답
     */
    static async getDocuments() {
        try {
            const response = await fetch(`${API_BASE_URL}/documents`, {
                method: 'GET'
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || '문서 목록 조회 실패');
            }

            return await response.json();
        } catch (error) {
            console.error('Get documents error:', error);
            throw error;
        }
    }

    /**
     * 문서 삭제
     * @param {string} documentId - 문서 ID
     * @returns {Promise<Object>} 삭제 응답
     */
    static async deleteDocument(documentId) {
        try {
            const response = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || '문서 삭제 실패');
            }

            return await response.json();
        } catch (error) {
            console.error('Delete error:', error);
            throw error;
        }
    }

    /**
     * 서버 상태 확인
     * @returns {Promise<Object>} 상태 응답
     */
    static async checkHealth() {
        try {
            const response = await fetch(`${API_BASE_URL}/health`, {
                method: 'GET'
            });

            if (!response.ok) {
                throw new Error('서버 연결 실패');
            }

            return await response.json();
        } catch (error) {
            console.error('Health check error:', error);
            throw error;
        }
    }
}
