/**
 * 认证 API
 */
import type { LoginRequest, TokenResponse } from '@/types'
import client from './client'

export const authApi = {
    /**
     * 登录
     */
    async login(data: LoginRequest): Promise<TokenResponse> {
        const response = await client.post<TokenResponse>('/admin/auth/login', data)
        return response.data
    },

    /**
     * 刷新 Token
     */
    async refresh(refreshToken: string): Promise<TokenResponse> {
        const response = await client.post<TokenResponse>('/admin/auth/refresh', {
            refreshToken,
        })
        return response.data
    },

    /**
     * 登出
     */
    async logout(): Promise<void> {
        await client.post('/admin/auth/logout')
    },
}
