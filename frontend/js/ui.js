// UI 컴포넌트 모듈

/**
 * UI 클래스
 */
class UI {
    /**
     * 로딩 오버레이 표시/숨김
     * @param {boolean} show - 표시 여부
     */
    static showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = show ? 'flex' : 'none';
    }

    /**
     * 업로드 진행률 표시
     * @param {boolean} show - 표시 여부
     * @param {number} progress - 진행률 (0-100)
     * @param {string} text - 진행 상태 텍스트
     */
    static showUploadProgress(show, progress = 0, text = '업로드 중...') {
        const progressDiv = document.getElementById('uploadProgress');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');

        progressDiv.style.display = show ? 'block' : 'none';
        if (show) {
            progressFill.style.width = `${progress}%`;
            progressText.textContent = text;
        }
    }

    /**
     * 문서 목록 렌더링
     * @param {Array} documents - 문서 목록
     */
    static renderDocumentList(documents) {
        const documentList = document.getElementById('documentList');

        if (!documents || documents.length === 0) {
            documentList.innerHTML = '<p class="empty-message">업로드된 문서가 없습니다.</p>';
            return;
        }

        documentList.innerHTML = documents.map(doc => `
            <div class="document-item" data-id="${doc.id}">
                <div class="document-name">
                    📄 ${doc.filename}
                </div>
                <div class="document-meta">
                    <span>페이지: ${doc.pages}</span>
                    <span>청크: ${doc.chunks}</span>
                </div>
                <div class="document-meta">
                    <span>${this.formatDate(doc.upload_date)}</span>
                </div>
                <button class="btn-delete" onclick="app.deleteDocument('${doc.id}')">
                    삭제
                </button>
            </div>
        `).join('');
    }

    /**
     * 날짜 포맷팅
     * @param {string} dateString - ISO 날짜 문자열
     * @returns {string} 포맷된 날짜
     */
    static formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) return '방금 전';
        if (minutes < 60) return `${minutes}분 전`;
        if (hours < 24) return `${hours}시간 전`;
        if (days < 7) return `${days}일 전`;

        return date.toLocaleDateString('ko-KR');
    }

    /**
     * 현재 시간 포맷팅
     * @returns {string} 포맷된 시간
     */
    static getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('ko-KR', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * 사용자 메시지 추가
     * @param {string} message - 메시지 내용
     */
    static addUserMessage(message) {
        const chatMessages = document.getElementById('chatMessages');

        // 환영 메시지 제거
        const welcomeMessage = chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';
        messageDiv.innerHTML = `
            <div class="message-avatar">👤</div>
            <div class="message-content">
                <div class="message-bubble">${this.escapeHtml(message)}</div>
                <div class="message-time">${this.getCurrentTime()}</div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    /**
     * AI 메시지 추가
     * @param {string} message - 메시지 내용
     * @param {Array} sources - 출처 문서 목록
     */
    static addAssistantMessage(message, sources = []) {
        const chatMessages = document.getElementById('chatMessages');

        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant';

        let sourcesHtml = '';
        if (sources && sources.length > 0) {
            sourcesHtml = `
                <div class="message-sources">
                    <div class="sources-title">📚 출처:</div>
                    ${sources.map(source => `
                        <div class="source-item">
                            • ${source.document} (페이지 ${source.page}) - 유사도: ${(source.score * 100).toFixed(1)}%
                        </div>
                    `).join('')}
                </div>
            `;
        }

        messageDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <div class="message-bubble">${this.formatMessage(message)}</div>
                ${sourcesHtml}
                <div class="message-time">${this.getCurrentTime()}</div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    /**
     * 로딩 메시지 추가
     * @returns {HTMLElement} 로딩 메시지 요소
     */
    static addLoadingMessage() {
        const chatMessages = document.getElementById('chatMessages');

        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant loading-message';
        messageDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <div class="message-bubble">답변을 생성하고 있습니다...</div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        return messageDiv;
    }

    /**
     * 로딩 메시지 제거
     */
    static removeLoadingMessage() {
        const loadingMessage = document.querySelector('.loading-message');
        if (loadingMessage) {
            loadingMessage.remove();
        }
    }

    /**
     * 에러 메시지 표시
     * @param {string} message - 에러 메시지
     */
    static showError(message) {
        const chatMessages = document.getElementById('chatMessages');

        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant';
        messageDiv.innerHTML = `
            <div class="message-avatar">⚠️</div>
            <div class="message-content">
                <div class="message-bubble" style="background-color: #ffe6e6; color: #cc0000;">
                    ${this.escapeHtml(message)}
                </div>
                <div class="message-time">${this.getCurrentTime()}</div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    /**
     * 채팅 영역을 맨 아래로 스크롤
     */
    static scrollToBottom() {
        const chatMessages = document.getElementById('chatMessages');
        setTimeout(() => {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 100);
    }

    /**
     * HTML 이스케이프
     * @param {string} text - 원본 텍스트
     * @returns {string} 이스케이프된 텍스트
     */
    static escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * 메시지 포맷팅 (줄바꿈 처리)
     * @param {string} text - 원본 텍스트
     * @returns {string} 포맷된 텍스트
     */
    static formatMessage(text) {
        return this.escapeHtml(text).replace(/\n/g, '<br>');
    }

    /**
     * 입력창 초기화
     */
    static clearInput() {
        const chatInput = document.getElementById('chatInput');
        chatInput.value = '';
        chatInput.style.height = 'auto';
    }

    /**
     * 전송 버튼 활성화/비활성화
     * @param {boolean} enabled - 활성화 여부
     */
    static setSendButtonEnabled(enabled) {
        const sendBtn = document.getElementById('sendBtn');
        sendBtn.disabled = !enabled;
    }

    /**
     * 토스트 메시지 표시
     * @param {string} message - 메시지
     * @param {string} type - 타입 (success, error, info)
     */
    static showToast(message, type = 'info') {
        // 간단한 토스트 메시지 구현
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background-color: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
            color: white;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        toast.textContent = message;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }
}
