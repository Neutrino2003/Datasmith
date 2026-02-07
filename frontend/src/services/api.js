export const API_BASE = '/api/v1';

export class API {
    static async request(endpoint, options = {}) {
        const url = `${API_BASE}${endpoint}`;

        const headers = { ...options.headers };

        // Auto-content-type for JSON if not FormData
        if (!(options.body instanceof FormData) && !headers['Content-Type']) {
            headers['Content-Type'] = 'application/json';
            if (options.body && typeof options.body === 'object') {
                options.body = JSON.stringify(options.body);
            }
        }

        try {
            const response = await fetch(url, { ...options, headers });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || errorData.error || `HTTP Error ${response.status}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }

            return response;
        } catch (error) {
            console.error(`API Request Failed: ${endpoint}`, error);
            throw error;
        }
    }

    static async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    static async post(endpoint, body) {
        return this.request(endpoint, { method: 'POST', body });
    }

    /**
     * Upload files with a message for analysis
     * @param {string} text - The message text
     * @param {File[]} files - Array of files to upload
     * @param {string} sessionId - Session identifier
     */
    static async uploadWithMessage(text, files, sessionId) {
        const formData = new FormData();
        formData.append('text', text || '');
        formData.append('session_id', sessionId);

        files.forEach((file, index) => {
            formData.append('files', file);
        });

        return this.request('/analyze/upload', {
            method: 'POST',
            body: formData
        });
    }
}
