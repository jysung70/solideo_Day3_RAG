// 메인 애플리케이션 로직

/**
 * App 클래스
 */
class App {
    constructor() {
        this.conversationId = null;
        this.init();
    }

    /**
     * 초기화
     */
    async init() {
        this.setupEventListeners();
        await this.loadDocuments();
        this.checkServerHealth();
    }

    /**
     * 이벤트 리스너 설정
     */
    setupEventListeners() {
        // 파일 업로드 버튼
        const uploadBtn = document.getElementById('uploadBtn');
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');

        uploadBtn.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileUpload(e.target.files[0]);
            }
        });

        // 드래그 앤 드롭
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileUpload(files[0]);
            }
        });

        // 채팅 입력
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendBtn');

        chatInput.addEventListener('input', () => {
            // 자동 높이 조절
            chatInput.style.height = 'auto';
            chatInput.style.height = chatInput.scrollHeight + 'px';

            // 전송 버튼 활성화/비활성화
            UI.setSendButtonEnabled(chatInput.value.trim().length > 0);
        });

        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });
    }

    /**
     * 서버 상태 확인
     */
    async checkServerHealth() {
        try {
            await API.checkHealth();
            console.log('서버 연결 성공');
        } catch (error) {
            console.error('서버 연결 실패:', error);
            UI.showError('서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.');
        }
    }

    /**
     * 파일 업로드 처리
     * @param {File} file - 업로드할 파일
     */
    async handleFileUpload(file) {
        // PDF 파일 확인
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            UI.showToast('PDF 파일만 업로드 가능합니다.', 'error');
            return;
        }

        try {
            // 진행률 표시
            UI.showUploadProgress(true, 0, '파일 업로드 중...');

            // 파일 업로드
            const uploadResponse = await API.uploadPDF(file);

            if (!uploadResponse.success) {
                throw new Error(uploadResponse.message);
            }

            UI.showUploadProgress(true, 50, '문서 처리 중...');

            // 문서 인덱싱
            const indexResponse = await API.indexDocument(uploadResponse.document_id);

            if (!indexResponse.success) {
                throw new Error(indexResponse.message);
            }

            UI.showUploadProgress(true, 100, '완료!');

            // 성공 메시지
            UI.showToast('문서가 성공적으로 업로드되었습니다.', 'success');

            // 문서 목록 새로고침
            await this.loadDocuments();

            // 진행률 숨기기
            setTimeout(() => {
                UI.showUploadProgress(false);
            }, 1000);

        } catch (error) {
            console.error('Upload error:', error);
            UI.showUploadProgress(false);
            UI.showToast(`업로드 실패: ${error.message}`, 'error');
        }
    }

    /**
     * 문서 목록 로드
     */
    async loadDocuments() {
        try {
            const response = await API.getDocuments();

            if (response.success && response.documents) {
                UI.renderDocumentList(response.documents);
            }
        } catch (error) {
            console.error('Load documents error:', error);
        }
    }

    /**
     * 문서 삭제
     * @param {string} documentId - 문서 ID
     */
    async deleteDocument(documentId) {
        if (!confirm('정말로 이 문서를 삭제하시겠습니까?')) {
            return;
        }

        try {
            UI.showLoading(true);

            const response = await API.deleteDocument(documentId);

            if (response.success) {
                UI.showToast('문서가 삭제되었습니다.', 'success');
                await this.loadDocuments();
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            console.error('Delete error:', error);
            UI.showToast(`삭제 실패: ${error.message}`, 'error');
        } finally {
            UI.showLoading(false);
        }
    }

    /**
     * 메시지 전송
     */
    async sendMessage() {
        const chatInput = document.getElementById('chatInput');
        const message = chatInput.value.trim();

        if (!message) {
            return;
        }

        // 사용자 메시지 표시
        UI.addUserMessage(message);
        UI.clearInput();
        UI.setSendButtonEnabled(false);

        // 로딩 메시지 표시
        UI.addLoadingMessage();

        try {
            // API 호출
            const response = await API.sendMessage(message, this.conversationId);

            // 로딩 메시지 제거
            UI.removeLoadingMessage();

            if (response.success) {
                // 대화 ID 저장
                if (response.conversation_id) {
                    this.conversationId = response.conversation_id;
                }

                // AI 응답 표시
                UI.addAssistantMessage(response.answer, response.sources);
            } else {
                throw new Error(response.message);
            }
        } catch (error) {
            console.error('Chat error:', error);
            UI.removeLoadingMessage();
            UI.showError(`오류가 발생했습니다: ${error.message}`);
        }
    }
}

// 애플리케이션 시작
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new App();
});
