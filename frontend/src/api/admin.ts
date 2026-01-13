/**
 * 管理员 API
 */
import type { AccessKeyInfo, StatsData } from '@/types';
import client from './client';

export const adminApi = {
    /**
     * 获取所有 Access Key
     */
    async getKeys(): Promise<{ success: boolean; data: AccessKeyInfo[] }> {
        const response = await client.get('/admin/keys')
        return response.data
    },

    /**
     * 手动验证 Key
     */
    async validateKey(keyId: number): Promise<{ success: boolean; data: { isValid: boolean; paintToken?: string } }> {
        const response = await client.post(`/admin/validate/${keyId}`)
        return response.data
    },

    /**
     * 获取统计信息
     */
    async getStats(): Promise<{ success: boolean; data: StatsData }> {
        const response = await client.get('/admin/stats')
        return response.data
    },
}
