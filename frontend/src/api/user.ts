/**
 * 用户 API
 */
import type { SubmissionStatus, SubmitRequest, SubmitResponse } from '@/types'
import client from './client'

export const userApi = {
    /**
     * 提交剪贴板信息
     */
    async submit(data: SubmitRequest): Promise<SubmitResponse> {
        const response = await client.post<SubmitResponse>('/submit', data)
        return response.data
    },

    /**
     * 批量提交剪贴板信息
     */
    async submitBatch(data: { pasteIds: string[]; submitterName?: string }): Promise<any> {
        const response = await client.post('/submit/batch', data)
        return response.data
    },

    /**
     * 查询提交状态
     */
    async getSubmissionStatus(submissionId: number): Promise<{ success: boolean; data: SubmissionStatus }> {
        const response = await client.get(`/submission/${submissionId}`)
        return response.data
    },
}
