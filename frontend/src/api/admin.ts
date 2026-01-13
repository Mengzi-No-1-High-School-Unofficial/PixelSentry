import apiClient from './client'

export const adminApi = {
    // 获取所有 Access Key
    async getKeys() {
        const response = await apiClient.get('/admin/keys')
        return response.data
    },

    // 获取统计信息
    async getStats() {
        const response = await apiClient.get('/admin/stats')
        return response.data
    },

    // 手动验证 Access Key
    async validateKey(keyId: number) {
        const response = await apiClient.post(`/admin/validate/${keyId}`)
        return response.data
    },

    // 重试失败的提交
    async retrySubmission(submissionId: number, forceFull: boolean = false) {
        const response = await apiClient.post(`/admin/retry/${submissionId}`, null, {
            params: { force_full: forceFull }
        })
        return response.data
    },

    // 获取所有提交记录
    async getSubmissions() {
        const response = await apiClient.get('/admin/submissions')
        return response.data
    },
}
